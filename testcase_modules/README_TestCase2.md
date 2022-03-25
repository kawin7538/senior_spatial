# Description for TestCase2

## Structure of input ```.json``` files

- Each ```.json``` file consists of ***2 line***. 
    - ***First Column*** list of 77 provinces.
    - ***Second line*** list of 77 values according to provinces sequence
    - all of these can be retrieved from https://kawin-hotcoldmaker.herokuapp.com/

## Output from this simulation

- ```dataframe_sim_output/mX.csv```<br>
output from poisson distribution with n columns where n is simulation amount.

- ```.exp_dist.png```<br>
Create directly from .json file, expected pattern

- ```.mean_dist.png```<br>
plot using average value of 100-replicate-poisson randomization

- ```.gistar.csv```<br>
Clustering results for all 100-replicate retrived from GiStar procedure, with most_cl means most cl type with voting procedure (mode), 3 labels: not-significant, hotspot, coldspot. These are considered at $\alpha$=0.05

- ```.gistar.png```<br>
Visualize of GiStar colorize with most occurrence results.

- ```.gistar.metrics.csv```<br>
Evaluation metrics in provincial level from GiStar for each replicate

- ```.gistar.metrics.precision.png```<br>
Plot of precision segregated with hotspot(red) and coldspot(blue)

- ```.gistar.metrics.recall.png```<br>
Plot of recall segregated with hotspot(red) and coldspot(blue)

- ```.gistar.metrics.accuracy.png```<br>
Plot of accuracy from GiStar procedure

- ```.localmoran.csv```<br>
Clustering results for all 100-replicate retrived from Local Moran procedure, with most_cl means most cl type with voting procedure (mode), 5 labels: ns, HH, LH, HL, LL. These are considered at $\alpha$=0.05

- ```.localmoran.png```<br>
Visualize of Local Moran colorize with most occurrence results.

## Description in each ```.json``` files (original testcases)

Each file will be simulated using poisson distribution with mu=provincial_mean*{1 if low, 2 if mid, 3 if high}

- ```m0.json```<br>
Sample Testcase, for system verification

- ```m1.json```<br>
Base case, neither higher nor lower

- ```m2.json```<br>
High value clusters at the west-central of Thailand

- ```m3.json```<br>
Similarly as m2, but 1 province was added as high value.

- ```m4.json```<br>
Higher at northern, last of southern, and southeast of northeastern, 2013- and 2019-like pattern, with incidence at southern

- ```m5.json```<br>
Thailand flag-like pattern, a province at higher value group is lower value one.

- ```m6.json```<br>
Higher at Petchbun, with lower of neighbors. include some incidence at some border.

- ```m7.json```<br>
Barcode-like pattern at southern, adapted from Testcase 1 from the old version.