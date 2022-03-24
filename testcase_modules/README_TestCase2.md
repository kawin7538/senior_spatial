# Description for TestCase

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

## Description in each ```.json``` files (original testcases)

Each file will be simulated using poisson distribution with mu=provincial_mean*{1 if low, 2 if mid, 3 if high}

- ```m0.json```<br>
Sample Testcase, for system verification

- ```m1.json```<br>
Base case, neither higher nor lower