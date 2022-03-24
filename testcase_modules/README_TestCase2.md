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

- ```.gi.csv```<br>
Clustering results for all 100-replicate retrived from GiStar procedure, with most_cl means most cl type with voting procedure (mode), 3 labels: not-significant, hotspot, coldspot, these are considered at $\alpha$=0.05

## Description in each ```.json``` files (original testcases)

Each file will be simulated using poisson distribution with mu=provincial_mean*{1 if low, 2 if mid, 3 if high}

- ```m0.json```<br>
Sample Testcase, for system verification

- ```m1.json```<br>
Base case, neither higher nor lower

- ```m2.json```<br>
High value clusters at the west-central of Thailand