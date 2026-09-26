# References

Documentation and material consulted while building this project, grouped by topic.

## Python standard library

- [pathlib: `Path.mkdir`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir): creating the dataset folders (`parents`, `exist_ok`) in `src/capture.py`.
- [datetime: `strftime` format codes](https://docs.python.org/3/library/datetime.html#format-codes): timestamped, collision-free photo file names in `src/capture.py`.

- [Python tutorial: classes](https://docs.python.org/3/tutorial/classes.html): `CapDecider` in `src/cap_decider.py`, an object that remembers recent answers between camera frames.
- [collections: `deque`](https://docs.python.org/3/library/collections.html#collections.deque): a list that keeps only the most recent items (the voting window).
- [collections: `Counter`](https://docs.python.org/3/library/collections.html#collections.Counter): counting items, used for totals in `src/live.py` and one way to count votes.

## Camera capture

- [OpenCV `cv::VideoCapture`](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html): opening a webcam by index or a network stream by URL, capture backends (DirectShow, Media Foundation, FFmpeg).

## Model training

- [PyTorch: installing locally](https://pytorch.org/get-started/locally/): choosing the CUDA build of PyTorch for an NVIDIA GPU.
- [PyTorch CUDA 13.0 wheel index](https://download.pytorch.org/whl/cu130): where the GPU builds of `torch` and `torchvision` are hosted.
- [PyTorch tutorial: transfer learning for computer vision](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html): why a model pretrained on ImageNet can be fine-tuned on a small dataset.
- [Ultralytics: image classification task](https://docs.ultralytics.com/tasks/classify/): YOLO classification models and how to train, validate and predict with them.
- [Ultralytics: classification dataset format](https://docs.ultralytics.com/datasets/classify/): the `train/`, `val/`, `test/` folder layout with one subfolder per class.
- [Ultralytics: train settings](https://docs.ultralytics.com/modes/train/#train-settings): every argument of `model.train()` and its default value.
- [torchvision `RandomResizedCrop`](https://docs.pytorch.org/vision/stable/generated/torchvision.transforms.RandomResizedCrop.html): the random crop Ultralytics applies to training images, and why its settings matter for this dataset.
- [Ultralytics: data augmentation guide](https://docs.ultralytics.com/guides/yolo-data-augmentation/): what each augmentation setting (`scale`, `erasing`, `flipud`, `fliplr`, `auto_augment`) does.
- [torchvision `RandomErasing`](https://docs.pytorch.org/vision/stable/generated/torchvision.transforms.RandomErasing.html): the black rectangles in the training batches, which can hide a defect.
- [torchvision `RandAugment`](https://docs.pytorch.org/vision/stable/generated/torchvision.transforms.RandAugment.html): the random rotations and colour changes applied to training images.
- [Zhong et al. (2017), *Random Erasing Data Augmentation*](https://arxiv.org/abs/1708.04896): the paper behind random erasing, which simulates objects being partly hidden.
- [Cubuk et al. (2019), *RandAugment: Practical automated data augmentation with a reduced search space*](https://arxiv.org/abs/1909.13719): the paper behind RandAugment.

## Evaluation

- [Ultralytics: predict mode](https://docs.ultralytics.com/modes/predict/): running a trained model on images and reading `result.probs` for classification.
- [Google ML Crash Course: accuracy, precision, recall](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall): the metrics printed by `src/evaluate.py`.
- [Google ML Crash Course: thresholds and the confusion matrix](https://developers.google.com/machine-learning/crash-course/classification/thresholding): how moving a decision threshold trades missed defects against false alarms.

## Image preprocessing

- [NumPy: indexing and slicing](https://numpy.org/doc/stable/user/basics.indexing.html): cropping an image with `frame[y1:y2, x1:x2]` in `src/preprocess.py`.
