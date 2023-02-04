path : C:\Users\Makaveli\Desktop\Work\RFO_farmbot\opencv\opencv\build\x64\vc15\bin

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

===== TRAINING 9-stage =====
<BEGIN
POS count : consumed   600 : 619
NEG count : acceptanceRatio    1200 : 0.00955247
Precalculation time: 1.351
+----+---------+---------+
|  N |    HR   |    FA   |
+----+---------+---------+
|   1|        1|        1|
+----+---------+---------+
|   2|        1|        1|
+----+---------+---------+
|   3|        1|        1|
+----+---------+---------+
|   4|        1|        1|
+----+---------+---------+
|   5|        1|        1|
+----+---------+---------+
|   6|        1|        1|
+----+---------+---------+
|   7| 0.996667|   0.9125|
+----+---------+---------+
|   8| 0.996667|   0.9125|
+----+---------+---------+
|   9| 0.996667| 0.880833|
+----+---------+---------+
|  10| 0.996667| 0.840833|
+----+---------+---------+
|  11| 0.996667|   0.8525|
+----+---------+---------+
|  12| 0.996667| 0.858333|
+----+---------+---------+
|  13| 0.996667| 0.824167|
+----+---------+---------+
|  14| 0.996667|    0.775|
+----+---------+---------+
|  15| 0.996667| 0.749167|
+----+---------+---------+
|  16| 0.996667| 0.739167|
+----+---------+---------+
|  17| 0.996667|     0.63|
+----+---------+---------+
|  18| 0.996667| 0.691667|
+----+---------+---------+
|  19| 0.996667| 0.620833|
+----+---------+---------+
|  20| 0.996667| 0.664167|
+----+---------+---------+
|  21| 0.996667|   0.6275|
+----+---------+---------+
|  22| 0.996667| 0.570833|
+----+---------+---------+
|  23| 0.996667|   0.5325|
+----+---------+---------+
|  24| 0.996667| 0.489167|
+----+---------+---------+
END>
Training until now has taken 0 days 0 hours 8 minutes 20 seconds.

HR - HIT RATE FA - FALSE ALARM
v poslednom layeri chceme mat FA co najmensie mozné cislo, ale bez ovetreiningu
Overtraining - Neg COUNT acceptance Ratio - ked je tam nieco ako 0.0000454651 - moze byt overtraining. ale 0.0035 je ok
