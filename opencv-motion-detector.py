ST_DIMENSION={"480":(640,480),"720":(1280,720),"1080":(1920,1080),"4K":(3840,2160)}
import cv2,pandas,time  #importing open cv module and pandas
from datetime import datetime
first_frame= None
status_list=[None,None]
times=[]
#dateframe to store the time values during which object detection and movement appears
df=pandas.DataFrame(columns=["Start","End"])

capture=cv2.VideoCapture(1) # creating a VideoCapture to capture live stream , argument 0 is the device index


print("SELECT YOUR VIDEO QUALITY :")
for i in ST_DIMENSION.keys():
    print(i)
vquality=input("Enter your opction : ")
if vquality not in ST_DIMENSION:
    vquality="480"
    print('Due to wrong selection Your Quatity is set to :',vquality)
else:
    print("Your Quatity is : ",vquality)
width,height=ST_DIMENSION[vquality]
capture.set(3,width)   # 3 is the id number of width
capture.set(4,height)  # 4 is the id number of height



while True:
    if first_frame is None:
        print('click ENTER to capture the first frame')
        _=input()
    check,frame = capture.read()
    #print(frame)
    status=0 #status at the eginning is Zero as the object is not visible
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) #converting each frame into gray sale image
    gray=cv2.GaussianBlur(gray,(21,21),0)  #converting gray scale frame to gaussianblur
    if first_frame is None:
        first_frame =gray
        continue
    delta_frame=cv2.absdiff(first_frame,gray)  #caliculating the diffrence between the first frame and other frames
    #if the diffrence value is less than 30 it will convert those pixels to black
    #if the diffrence value is grater than 30 it will convert those pixels to black
    thresh_delta = cv2.threshold(delta_frame,30,255,cv2.THRESH_BINARY)[1]
    thresh_delta=cv2.dilate(thresh_delta,None,iterations=0)

    #defining the countour area basically, add the boarders
    (cnts,_)=cv2.findContours(thresh_delta.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    #Removes noise and shadows , Basically it will keep only that part white, which has area greater than 1000 pixels
    for contour in cnts:
        if cv2.contourArea(contour)<1000:
            continue
        status=1
        #creates a rectangular box around the object in the frame
        (x,y,w,h)=cv2.boundingRect(contour)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)

    status_list.append(status) #status after every frame is updated and only last 2 are kept in it
    status_list=status_list[-2:]

    #checking for the last 2 states to save the time
    if status_list[-1]==1 and status_list[-2]==0:
        times.append(datetime.now())
    if status_list[-1]==0 and status_list[-2]==1:
        times.append(datetime.now())

    # displaying all the frames
    cv2.imshow('frame',frame)
    cv2.imshow('capturing',gray)
    cv2.imshow('delta',delta_frame)
    cv2.imshow('thresh',thresh_delta)

    key=cv2.waitKey(1) #the frame will be for 1us

    if key == ord('q'):
        if status==1:
            times.append(datetime.now())
        break


print(status_list)
print(times)
#stroring time values in a dataframe
for i in range(0, len(times), 2):
    df = df.append({"Start": times[i], "End": times[i + 1]}, ignore_index=True)
df.to_csv("Times.csv") #writing the dataframe to a CSV file

capture.release()
cv2.destroyAllWindows()