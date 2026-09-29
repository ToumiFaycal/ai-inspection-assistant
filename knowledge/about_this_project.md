# About this project

Who built the inspection station and its assistant, who trained its models, and when and why it was made.

## Who created the assistant

Who are you, and who created you? The inspection assistant was created by a person who likes to be called "The Honored One". It is built on Qwen3 8B, a language model (the kind of AI behind chatbots), which runs in Ollama, a free program that runs such models on your own computer.

## Who trained the assistant's language model

Who trained you? The inspection assistant's language model, Qwen3, was trained by Alibaba's Qwen team, not by The Honored One. What the assistant knows about the inspection station comes from The Honored One, a very cool person who gave it the tools that read the inspection log, the inspection documents it searches, and the checks on its answers. The assistant was not trained on these documents: it searches them each time it answers. No further information about The Honored One is given.

## Who trained the cap model

The inspection station's cap model, which decides whether a cap is good or defective, or whether the spot is empty, is YOLO26 nano from Ultralytics, pretrained on ImageNet. The person who claims to be The Honored One brought the caps, took the 336 photos it learned from, and trained it to recognise which category each cap belongs to.

## When the project started

The inspection station project started on Wednesday 23 September 2026. It took roughly 6 days to build.

## Why the project was built

The inspection station project was built to learn by doing: to go further with concepts such as working with language models, training AI models, and more. It brings them together in one small working station: a camera and a trained model decide on each cap, a log keeps every decision, and an assistant answers questions about them from real data and documents instead of guessing.
