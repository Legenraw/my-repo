import numpy as np
from typing import Tuple
from src.controllers.vehicle_controller import VehicleController, GameState
from src.controllers import pid
import cv2 as cv
import math
import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.transforms import ToTensor


class PIDControllerGame1(VehicleController):
    def _init_(self, config):
        super()._init_(config)
        self.fmag=0
        self.fpid=pid.PID_controller(200000,2,1)
        self.amag=0
        self.apid=pid.PID_controller(10000,0,250)
        self.a=0
        self.shape_history={}
        self.number_history={}


        device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
        training_data = datasets.MNIST(
                root="data",
                train=True,
                download=True,
                transform=ToTensor()
        )

        test_data = datasets.MNIST(
                root="data",
                train=False,
                download=True,
                transform=ToTensor()
        )
        train_dataloader = DataLoader(training_data, batch_size=64)
        test_dataloader = DataLoader(test_data, batch_size=64)
        learning_rate = 1e-3
        batch_size = 200
        epochs = 5

        class NeuralNetwork(nn.Module):
            def _init_(self):
                super()._init_()
                self.flatten = nn.Flatten()
                self.linear_relu_stack = nn.Sequential(
                    nn.Linear(28*28, 512),
                    nn.ReLU(),
                    nn.Linear(512, 512),
                    nn.ReLU(),
                    nn.Linear(512, 10),
                )

            def forward(self, x):
                x = self.flatten(x)
                logits = self.linear_relu_stack(x)
                return logits
        def train_loop(dataloader, model, loss_fn, optimizer):
            size = len(dataloader.dataset)
            # Set the model to training mode - important for batch normalization and dropout layers
            # Unnecessary in this situation but added for best practices
            model.train()
            for batch, (X, y) in enumerate(dataloader):
                # Compute prediction and loss
                pred = model(X)
                loss = loss_fn(pred, y)
                # Backpropagation
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                if batch % 100 == 0:
                    loss, current = loss.item(), batch * batch_size + len(X)
                    print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")
            
        def test_loop(dataloader, model, loss_fn):
            # Set the model to evaluation mode - important for batch normalization and dropout layers
            # Unnecessary in this situation but added for best practices
            model.eval()
            size = len(dataloader.dataset)
            num_batches = len(dataloader)
            test_loss, correct = 0, 0
        
            # Evaluating the model with torch.no_grad() ensures that no gradients are computed during test mode
            # also serves to reduce unnecessary gradient computations and memory usage for tensors with requires_grad=True
            with torch.no_grad():
                for X, y in dataloader:
                    pred = model(X)
                    test_loss += loss_fn(pred, y).item()
                    correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        
            test_loss /= num_batches
            correct /= size
            print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

        self.model = NeuralNetwork()
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=learning_rate)
        
        self.model.load_state_dict(torch.load("mnist_model.pth"))
        self.model.eval()

    def compute_control(self, state: GameState) -> Tuple[np.ndarray, float]:
        #game 4
        active_nums={}

        frame=cv.cvtColor(state.screen_frame,cv.COLOR_RGB2BGR)
        white_img=255*np.ones(frame.shape[:2],dtype='uint8')

        mask1=cv.rectangle(white_img,(0,0),(220,150),0,-1)
        mask2=cv.rectangle(mask1,(0,620),(180,720),0,-1)
        masked_img=cv.bitwise_and(frame,frame,mask=mask2)

        gray=cv.cvtColor(masked_img, cv.COLOR_BGR2GRAY)
        canny=cv.Canny(gray,100,150)

        contours,hierarchies=cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        resized=np.zeros(masked_img.shape[:2],dtype='uint8')

        for i,contour in enumerate(contours):
            if cv.contourArea(contour)<900:
                continue
            epsilon=0.03*cv.arcLength(contour,True)
            approx=cv.approxPolyDP(contour,epsilon,True)
            digit_frame=0
            if len(approx)==4:
                x,y,w,h=cv.boundingRect(approx)
                coords=(y+h/2,x+w/2)
                img=gray[y:y+h,x:x+w]
                resized=cv.resize(img,(28,28))
                t,threshold=cv.threshold(resized,1,255,cv.THRESH_BINARY)
                tens = torch.from_numpy(threshold).float()
                tens = tens.unsqueeze(0).unsqueeze(0)
                if coords not in active_nums:
                        dx=coords[1]-state.vehicle_position[0]
                        dy=coords[0]-state.vehicle_position[1]
                        dist_val=math.sqrt(dx*dx + dy*dy)
                        active_nums[coords]=(torch.argmax(self.model(tens)).item()/dist_val)
        point_wise_coords={}
        point_list=[]
        for coord in active_nums:
            if not coord in self.number_history:
                self.number_history[coord]=1
            point_wise_coords[active_nums[coord]]=coord
            point_list.append((active_nums[coord]*self.number_history[coord]))
        point_list.sort()
        thresh2=gray.copy()
        xpos=int(state.vehicle_position[0])
        ypos=int(state.vehicle_position[1])
        thresh2[ypos-10:ypos+10,xpos-10:xpos+10]=255
        cv.imshow('th',thresh2)
        cv.waitKey(1)

        if point_list:
            #computing force
            target=point_wise_coords[point_list[-1]]
            delx=target[1]-state.vehicle_position[0]
            dely=target[0]-(state.vehicle_position[1])
            aSet=np.arctan2(dely,delx)
            direction=np.array([np.cos(aSet),-1*np.sin(-1*aSet)])
            error=math.sqrt((delx*delx)+(dely*dely))
            change=self.fpid.total_action(error,0.016)
            self.fmag+=change
            #computing force

            #checking if target is reached
            if error<10:
                self.number_history[target]=-1
            #checking if target is reached

            #computing torque
            aError = aSet - state.vehicle_orientation
            errorMag = 0
            if(aError<-1*np.pi or (aError>0 and aError<np.pi)):
                errorMag=aError%(2*np.pi)
            else:
                errorMag=-1*((2*np.pi-aError)%(2*np.pi))
            achange=self.apid.total_action(errorMag,0.016)
            self.amag=achange

            print(state.vehicle_position)
            return self.fmag*direction, self.amag
            #computing torque


        # Computing Force
        #frame=cv.cvtColor(state.screen_frame,cv.COLOR_RGB2BGR)
        #white_img=255*np.ones(frame.shape[:2],dtype='uint8')
        #mask1=cv.rectangle(white_img,(0,0),(220,150),0,-1)
        #mask2=cv.rectangle(mask1,(0,650),(180,720),0,-1)
        #mask2=cv.rectangle(mask11,(int(state.vehicle_position[0]-15),int(state.vehicle_position[1]-15)),(int(state.vehicle_position[0]+15),int(state.vehicle_position[1]+15)),0,-1)
    
        #gray=cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        #k,thresh=cv.threshold(gray,200,220,cv.THRESH_BINARY)
#
        #masked_img=cv.bitwise_and(frame,frame,mask=mask2)
        ##masked_and_dilated=cv.dilate(masked_img,(3,3),iterations=1)
        ##masked_eroded=cv.erode(masked_and_dilated,(3,3),iterations=1)
        #gray=cv.cvtColor(masked_img, cv.COLOR_BGR2GRAY)
        #k,thresh=cv.threshold(gray,200,220,cv.THRESH_BINARY)
        #contours,hierarchies=cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        #active_shapes={}
        #for i,contour in enumerate(contours):
        #    if i==0:
        #        continue
        #    epsilon=0.03*cv.arcLength(contour,True)
        #    approx=cv.approxPolyDP(contour,epsilon,True)
        #    cv.drawContours(masked_img,contour,0,(200,0,0),20)
#
        #    x,y,w,h=cv.boundingRect(approx)
        #    x_mid=int(x+w/2)
        #    y_mid=int(y+h/2)
#
        #    coords=(y_mid,x_mid)
        #    colour=(255,255,255)
        #    font=cv.FONT_HERSHEY_COMPLEX
#
        #    colour_mult=0
        #    if masked_img[y_mid][x_mid][0]>0:
        #        colour_mult=1
        #    elif masked_img[y_mid][x_mid][1]>0:
        #        colour_mult=1.5
        #    elif masked_img[y_mid][x_mid][2]>0:
        #        colour_mult=0.5
        #    
        #    shape_mult=0
        #    if len(approx)==3:
        #        shape_mult=2
        #    elif len(approx)==4:
        #        shape_mult=1.5
        #    else:
        #        shape_mult=1
        #    dx=coords[1]-state.vehicle_position[0]
        #    dy=coords[0]-state.vehicle_position[1]
        #    dist_val=math.sqrt(dx*dx + dy*dy)
        #    total_mult=shape_mult*colour_mult*(1/dist_val)
        #    active_shapes[coords]=total_mult
        #    #if masked_img[y_mid][x_mid]==(255,0,0):
        #    #    shape_colour='blue'
        #    #if(len(approx)==3):
        #    #    cv.putText(thresh,'t',coords,font,1,colour,1)
        #    #    print(shape_colour)
        #    #elif(len(approx)==4):
        #    #    cv.putText(thresh,'r',coords,font,1,colour,1)
        #    #    print(shape_colour)
        #    #else:
        #    #    cv.putText(thresh,'c',coords,font,1,colour,1)
        #    #    print(shape_colour)
        #point_wise_coords={}
        #point_list=[]
        #for coord in active_shapes:
        #    if not coord in self.shape_history:
        #        self.shape_history[coord]=1
        #    point_wise_coords[active_shapes[coord]]=coord
        #    point_list.append(active_shapes[coord]*self.shape_history[coord])
        #point_list.sort()
        #thresh2=thresh.copy()
        #xpos=int(state.vehicle_position[0])
        #ypos=int(state.vehicle_position[1])
        #print(type[thresh2])
        #thresh2[ypos-10:ypos+10,xpos-10:xpos+10]=255
        #cv.imshow('th',thresh2)
        #cv.waitKey(1)
#
        #if point_list:
        #    #computing force
        #    target=point_wise_coords[point_list[-1]]
        #    delx=target[1]-state.vehicle_position[0]
        #    dely=target[0]-(state.vehicle_position[1])
        #    aSet=np.arctan2(dely,delx)
        #    direction=np.array([np.cos(aSet),-1*np.sin(-1*aSet)])
        #    error=math.sqrt((delx*delx)+(dely*dely))
        #    change=self.fpid.total_action(error,0.016)
        #    self.fmag+=change
        #    #computing force
#
        #    #checking if target is reached
        #    if error<10:
        #        self.shape_history[target]=-1
        #    #checking if target is reached
#
        #    #computing torque
        #    aError = aSet - state.vehicle_orientation
        #    errorMag = 0
        #    if(aError<-1*np.pi or (aError>0 and aError<np.pi)):
        #        errorMag=aError%(2*np.pi)
        #    else:
        #        errorMag=-1*((2*np.pi-aError)%(2*np.pi))
        #    achange=self.apid.total_action(errorMag,0.016)
        #    self.amag=achange
#
        #    print(state.vehicle_position)
        #    return self.fmag*direction, self.amag
        #    #computing torque
    #
#
        ## Obstacle avoid
#
        ##extra_force=np.array([0.0,0.0])
        ##for item in state.obstacles:
        ##    k=7000000000
        ##    minD=200
        ##    dx=state.vehicle_position[0]-item.position[0]
        ##    dy=state.vehicle_position[1]-item.position[1]
        ##    r=np.sqrt(dx*dx + dy*dy)
        ##    if(r<minD):
        ##        extra_force[0]+=((k*dx)/r)((1/r)-(1/minD))((1/r)-(1/minD))
        ##        extra_force[1]+=((k*dy)/r)((1/r)-(1/minD))((1/r)-(1/minD))
        ##    else:
        ##        extra_force[0]+=0
        ##        extra_force[1]+=0
        ##print(state.distance_to_target)
#
        ## Obstacle avoid
        #self.a+=1
        return np.array([0.0, 0.0]), 0.0

    def reset(self):
        self.last_pos_error = np.array([0.0, 0.0])
        self.last_orientation_error = 0.0
