from subprocess import call
import speech_recognition as SpeechR
import serial
import RPi.GPIO as GPIO      
import os, time
r= SpeechR.Recognizer()

led = 23

text = {}
text1 = {}
step_sleep = 0.002
rotations = 5
step_count = 4096 # 5.625*(1/64) per step, 4096 steps is 360°
motor_pins = [17,18,27,22]
#global motor_step_counter = 0
StepSeq = [[1,0,0,1],[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1]]
StepCount = 8
StepState = 0


FlrOne = ["one","first","ground","1","1st"]
FlrTwo = ["two","second","2","2nd", "middle"]
FlrThree = ["three","third","top","3","3rd"]
Flrcurr = 1


GPIO.setmode( GPIO.BCM )
GPIO.setup( led, GPIO.OUT )
GPIO.output( led, GPIO.LOW )

for index in range(0, len(motor_pins)):
    GPIO.setup( motor_pins[index], GPIO.OUT )
    GPIO.output( motor_pins[index], GPIO.LOW )

def cleanup():
    GPIO.output( motor_pins[0], GPIO.LOW )
    GPIO.output( motor_pins[1], GPIO.LOW )
    GPIO.output( motor_pins[2], GPIO.LOW )
    GPIO.output( motor_pins[3], GPIO.LOW )
    GPIO.output( led, GPIO.LOW )
    GPIO.cleanup()

def Motor_Step(Direction,flrLeaps):
    motor_step_counter = 0
    if Direction == "UP":
        print("UP")
        for i in range(0, (step_count*flrLeaps*rotations)):
            for pin in range(0, len(motor_pins)):
                GPIO.output( motor_pins[pin], StepSeq[motor_step_counter][pin] )
            motor_step_counter = (motor_step_counter - 1) % 8
            time.sleep(step_sleep)
    elif Direction == "DWN":
        print("DWN")
        for i in range(0, (step_count*flrLeaps*rotations)):
            for pin in range(0, len(motor_pins)):
                GPIO.output( motor_pins[pin], StepSeq[motor_step_counter][pin] )
            motor_step_counter = (motor_step_counter + 1) % 8
            time.sleep(step_sleep)
    else: # defensive programming
            print( "uh oh... direction should *always* be either UP or DWN" )
            cleanup()
            exit(1)

def FlrEval(target):
    global Flrcurr
    if(target != Flrcurr):
        if(Flrcurr == 1 and target == 2):
            Motor_Step("UP",1)
            Flrcurr = 2
        elif(Flrcurr == 1 and target == 3):
            Motor_Step("UP",2)
            Flrcurr = 3
        elif(Flrcurr == 2 and target == 1):
            Motor_Step("DWN",1)
            Flrcurr = 1
        elif(Flrcurr == 2 and target == 3):
            Motor_Step("UP",1)
            Flrcurr = 3
        elif(Flrcurr == 3 and target == 2):
            Motor_Step("DWN",1)
            Flrcurr = 2
        elif(Flrcurr == 3 and target == 1):
            Motor_Step("DWN",2)
            Flrcurr = 1
        else:
            print("Evaluvation  error")


    else:
        print("State a different floor")
        call(["espeak", "-s140  -ven+18 -z" , "Please state a different floor other than current floor"])


def listen1():
    with SpeechR.Microphone(device_index = 1) as source:
               r.adjust_for_ambient_noise(source)
               print("Say Something")
               #audio = r.listen(source) #audio_out = r.record(source, duration=4)
               audio = r.record(source, duration=4)
               print("got it")
    return audio
def voice(audio1):
       try: 
         text1 = r.recognize_google(audio1) 
##         call('espeak '+text, shell=True) 
         print ("you said: " + text1)
         return text1; 
       except SpeechR.UnknownValueError: 
          call(["espeak", "-s140  -ven+18 -z" , "The Speech Recognition Engine could not understand"])
          print("Speech Recognition Engine could not understand") 
          return 0
       except SpeechR.RequestError as e: 
          print("Could not request results from Server")
          return 0

def main(text):
    print ("Which Floor to Head to?")
    audio1 = listen1() 
    text = str(voice(audio1))
    print(text)
    for x in range(0, len(FlrOne)):
        if str(FlrOne[x]) in text:
            GPIO.output(led , 1)
            call(["espeak", "-s140  -ven+18 -z" , "okay  Sir, Moving To Floor 1"])
            print ("Moving To Floor 1")
            FlrEval(1)
            text = {}
            GPIO.output(led , 0)
    for y in range(0, len(FlrTwo)):
        if str(FlrTwo[y]) in text:
            GPIO.output(led , 1)
            call(["espeak", "-s140  -ven+18 -z" , "okay  Sir, Moving To Floor 2"])
            print ("Moving To Floor 2")
            FlrEval(2)
            text = {}
            GPIO.output(led , 0)
    for z in range(0, len(FlrThree)):
        if str(FlrThree[z]) in text:
            GPIO.output(led , 1)
            call(["espeak", "-s140  -ven+18 -z" , "okay  Sir, Moving To Floor 3"])
            print ("Moving To Floor 3")
            FlrEval(3)
            text = {}
            GPIO.output(led , 0)


if __name__ == '__main__':
    try:
        while(1):
            audio1 = listen1() 
            text = voice(audio1)
            if text == 'hello': ## Wake Word
                text = {}
                call(["espeak", "-s140  -ven+18 -z" ," Hi there, waiting for your command"])
                call(["espeak", "-s140  -ven+18 -z" ," Where would you like to go"])
                main(text)
            #elif len(text) == 0:
            #    call(["espeak", "-s140 -ven+18 -z" , " Sorry Didn't catch that Please repeat"])
            else:
                print("looping")
    except KeyboardInterrupt:
        call(["espeak", "-s140 -ven+18 -z" , "Exiting the process Shutting down"])

    finally:
        GPIO.cleanup() # this ensures a clean exit  

