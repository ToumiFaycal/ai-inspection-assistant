# Known limitations

What the inspection station does not do well yet, and what could improve it.

## Dark caps with thin scratches

A dark brown cap with a grainy, metallic-looking top was called good with full confidence even after it was scratched. Its thin scratches are dark lines on a dark, grainy surface, and no cap like it was in the training photos. The model can be very sure of itself on caps unlike anything it has seen, and still be wrong.

## Subtle rim defects

The two defective photos missed in the final test show the same cap, whose rim is only slightly bent. From some angles the bent part looks like a thin strip at the edge and the top looks normal. The training photos had few examples of subtle rim defects on this kind of cap.

## Only what is visible from above

The camera only sees the top face and the outline of the cap. Defects on the side or underneath the cap, such as a broken tamper ring, damaged threads or damage inside the cap, cannot be detected.

## Setup and lighting must stay the same

The model was trained with one camera position, one lamp and no daylight. Changing any of them can change its answers. The phone also adjusts its colours automatically, and a large brightly coloured cap can make the background look tinted.

## Very slow movements

The stillness check compares each video frame with the one just before. A cap pushed extremely slowly can change so little between two frames that it looks still, and be decided before it is in place.

## Grainy caps and the motion threshold

On caps with a very grainy surface, a still picture can measure up to about 2.8 on the motion scale, close to the 3.0 limit. A cap even grainier than that could look like it is moving all the time and never be decided.

## A small dataset

The model learned from 336 photos of about 28 caps. The validation photos had mostly obvious defects, so the threshold was chosen on an easier set of photos than the final test.

## Caps unlike the training caps

The model only knows the kinds of caps it was trained on: mostly blue and red caps, plus a few white, black, pink and green ones. Caps with a different colour, material, size or surface, or with an unusual kind of damage, may not be recognised well. The fix is to train the model on more and more varied caps. That is not planned: this station is a learning project, and collecting a large set of caps is outside its purpose.

## A learning project, not a product

This inspection station is a personal learning and demonstration project. It shows how the pieces of an inspection system fit together: a camera, a trained model, stable decisions, a log and an assistant. It was built with about 28 caps, a phone and a cardboard box, and it is not meant to inspect caps in a real factory.

## The assistant's general knowledge

The inspection assistant runs on a language model that can state wrong facts with confidence. It is set up to answer from the inspection log and from these documents, not from its general knowledge.

## Possible improvements

These are ideas for making the station more reliable, not plans:
- Train with more dark caps (brown, black, dark green) and more subtle rim defects, and make the validation photos as hard as real use.
- Light the cap from a low angle (raking light), which makes scratches and dents stand out.
- Lock the phone's white balance and exposure so colours stay the same.
- Save the image of every decided cap, for checking by hand and as new training photos.
