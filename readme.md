**TODO:** Use Deep-Neural-Network instead of te cascade classifier for much better real-time performance(YOLOv5)

OpenCV commands/stuff
```path to opencv : C:\Users\Makaveli\Desktop\Work\RFO_farmbot\opencv\opencv\build\x64\vc15\bin

Create bounding boxes -> C:\Users\Makaveli\Desktop\Work\RFO_farmbot\opencv\opencv\build\x64\vc15\bin\opencv_annotation.exe --annotations=positive.txt --images=positive/

create vectors ->
 C:\Users\Makaveli\Desktop\Work\RFO_farmbot\opencv\opencv\build\x64\vc15\bin\opencv_createsamples.exe -info positive.txt -w 24 -h 24 -num 500 -vec positive.vec

 -w / -h rozmery detection window. Mensie ako toto nenajde. Vacsie cslo = lepsi vysledok? ale pomalesie a dlhsie trenuje
 -num musi byt vacsie ako pocet bounding boxov 

 train model ->
 C:\Users\Makaveli\Desktop\Work\RFO_farmbot\opencv\opencv\build\x64\vc15\bin\opencv_traincascade.exe -data cascadeTrainerOutput/ -vec positive.vec -bg negative.txt -w 24 -h 24 -maxFalseAlarmRate 0.3 -minHitRate 0.999 -precalcValBufSize 6000 -precalcIdxBufSize 6000 -numPos 600 -numNeg 1200 -numStages 15

 -numpos - pocet pozitivnych samplov - cislo mensie ako pocet samplov
 -numNeg - pocet engativnich samplov - moze byt vacsie ako pocet negativnych samplov lebo to vzorkuje na mensie (2x mensie ako numpos alebo 2x vacsie who knows)
 -numStages pocet stagov vacsie moze byt lepsi model ale nemusi


HR - HIT RATE FA - FALSE ALARM
v poslednom layeri chceme mat FA co najmensie mozné cislo, ale bez ovetreiningu
Overtraining - Neg COUNT acceptance Ratio - ked je tam nieco ako 0.0000454651 - moze byt overtraining. ale 0.0035 je ok
```
