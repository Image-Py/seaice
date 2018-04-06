Ice HD>None
Duplicate>{'name': 'block', 'stack': True}
Sobel>{'axis': 'both'}
Gaussian>{'sigma': 3.0}
Multiply>{'num': 3.0}
Find Minimum>{'tol': 10, 'mode': False, 'wsd': False}
Watershed With ROI>{'sigma': 0, 'type': 'white line', 'con': False, 'ud': True}
Select None>None
Invert>None
Intensity Filter>{'con': '4-connect', 'inten': 'Ice HD', 'max': 0.0, 'min': 0.0, 'mean': 70.0, 'std': 0.0, 'sum': 0.0, 'front': 255, 'back': 0}
Binary Erosion>{'w': 3, 'h': 3}
Duplicate>{'name': 'line', 'stack': True}
Binary Dilation>{'w': 3, 'h': 3}
Binary Outline>None
Binary Dilation>{'w': 3, 'h': 3}
Set Background>{'img': 'Ice HD', 'op': 'Clip', 'k': 1.0, 'kill': False}