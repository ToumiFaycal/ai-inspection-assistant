# References

Documentation and material consulted while building this project, grouped by topic.

## Python standard library

- [pathlib: `Path.mkdir`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir): creating the dataset folders (`parents`, `exist_ok`) in `src/capture.py`.
- [datetime: `strftime` format codes](https://docs.python.org/3/library/datetime.html#format-codes): timestamped, collision-free photo file names in `src/capture.py`.

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
