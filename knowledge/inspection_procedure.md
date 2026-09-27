# Inspection procedure

How to run the inspection station and inspect caps, step by step.

## The station setup

The station is a cardboard box. The phone rests on top of it and looks straight down through a hole in the top, at the floor of the box, where the caps are placed. A single lamp lights the inside through a large opening in the left side of the box, and daylight is kept out (curtains closed, room lights off), so that every photo is lit the same way. The inspection spot is not marked: caps are always placed in the same place, in the centre of the camera view. The phone streams its video over Wi-Fi with the IP Webcam app.

## Before starting

Check that nothing in the setup has moved: the phone and its angle, the box and the lamp. The model was trained with this exact setup, so a moved camera or a different light makes its answers less reliable. A cap placed should appear centred and fill most of the square shown on screen.

## Starting the station

1. On the phone, open IP Webcam and start its server.
2. On the computer, start the live inspection with `python src/live.py`.
3. A window opens showing the square the model looks at.

## Placing a cap

Place the cap **top face up**, in the usual place in the centre of the camera view, then **take your hand away and keep the cap still**. The station only makes a decision once the picture has stopped moving, so there is no need to hurry. Do not move the cap until the decision appears. Avoid pushing the cap into place extremely slowly: very slow movements can look still to the station (see the known limitations).

## Reading the screen

- The top line shows the model's answer for the current video frame and its probability that the cap is defective.
- Below it, the station's state: **WAITING** (nothing on the spot), **COLLECTING** (checking the cap), **DECIDED** (a decision was made).
- The motion line turns orange while something moves in the picture.
- At the bottom: the decision for the **last cap**, and the number of good and defective caps so far.

## After a decision

Remove the cap from the spot. The station waits until the spot has been empty for a moment, then it is ready for the next cap. Keep defective caps apart from good ones.

## Unsure rejects

If a cap sits still for about 2 seconds and the station still cannot decide, it rejects the cap as a precaution and shows **"unsure: check this cap by hand"**. Set the cap aside and check it by eye, using the defect definitions.

## Where decisions are saved

Every decision is saved in the inspection log with its time, the decision (good or defective), its confidence and its reason ("vote" for a normal decision, "unsure" for a precautionary reject). To see the latest decisions, run `python src/inspection_log.py`, or ask the inspection assistant.

## Stopping the station

Click the inspection window and press **q**.
