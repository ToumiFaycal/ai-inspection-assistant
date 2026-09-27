# Tuning notes

Why the inspection station is set up the way it is, and how its numbers were chosen.

## The model

The station uses a small image classification model (YOLO, "nano" size) that was first trained on a large public collection of everyday photos, then fine-tuned on 336 photos of bottle caps taken with the station's own camera. It looks at the photo and gives a probability for each answer: good, defective or empty.

## The photos and how they were split

The 336 photos come from about 28 different caps. Each cap was photographed good first, then damaged and photographed again as defective, so both answers have the same colours and brands. The photos were split **by physical cap**: a cap used for training never appears in the photos used to check the model, so the model is never tested on a cap it has already seen.

## The inspection square

Every photo is cut down to the central square of the camera view (720 by 720 pixels) before the model sees it, because the cap always sits in the same place. The same crop is used for training and for live inspection.

## Training choices

During training, the photos are randomly flipped and rotated so that the model learns that a cap can sit in any orientation. Two common training tricks were switched off: random cropping and random black rectangles. On these photos they could cut off or hide the defect, and teach the model that a cap was defective without showing why. Switching them off improved the results on the validation photos from 58 of 60 to 60 of 60 correct.

## Test results

On 65 test photos the model had never seen, it gave the right answer for 63 of them (96.9%). Every cap it called defective really was defective (precision 100%), and it caught 23 of the 25 defective photos (recall 92%). All 25 good photos and all 15 empty photos were correct. The 2 missed photos show the same cap, which has a subtly bent rim.

## The defect threshold

A cap is called defective when the model's probability of "defective" is **at least 0.4**, instead of the usual 0.5. The threshold is lower on purpose: a missed defect costs more than a false alarm. It was chosen on the validation photos, where every value from 0.4 to 0.6 gave perfect results, and 0.4 is the most cautious of them. It was then frozen before the final test, and must not be changed based on test results.

## Deciding once per cap

A single video frame can be wrong, for example while a hand is still in view. So the station lets the last **15 frames** vote (about half a second of video), and a cap is decided only when at least **12 of them agree** (80%).

## The stillness check

Frames only count as votes while the picture is **still**. The station compares each frame with the previous one and measures the average change in brightness per pixel, on a scale from 0 (identical) to 255 (completely different). Above **3.0**, the picture counts as moving and the votes start again. The value 3.0 was chosen from live readings: an empty spot measures about 1.5, smooth caps less than 2, grainy dark caps up to about 2.8, and a moving hand much more.

## The "when in doubt, reject" timeout

If a cap stays still for **60 frames** (about 2 seconds) and the frames still do not agree, the station rejects it as a precaution, with the reason "unsure", so that a person can check it.

## Removing a cap

The station considers a cap removed after **10 empty frames in a row**, then waits for the next cap.

## Confidence in the log

The confidence saved with each decision is the share of the voting frames that agreed with it: 1.00 when all 15 frames agreed, at least 0.80 for a normal decision, and lower for an "unsure" reject.
