# Description for TestCase

## Iteration through value precise
all the inputs will be iterately with precise value from 100, 95, 90, 75 percent

## Structure of ```.in``` files

- Each ```.in``` file consists of ***2 line***. 
    - ***First line*** contains four parameters as follow: layer depth for preparing data, layer depth for filter, filter property (name, etc.), and percent adjust (0-100) that defined for random interval.
    - ***Second line*** consists of n classified values for n nodes in map, input as "high" and "low".

## Description in each ```.in``` files (original testcases)

- ```1-2.in```
Prachuap Khiri Khan, segregated pattern.

- ```3-4.in```
Prachuap Khiri Khan, grouped pattern.

- ```5-7.in```
Prachuap Khiri Khan, drumbell shape, heavy-outside.

- ```8-10.in```
Prachuap Khiri Khan, drumbell shape, heavy-inside.

- ```11-13.in```
Phuket, low-value-dominant.

- ```14-16.in```
Phuket, high-value-dominant.

- ```17.in```
Pathum Thani, complete segregated

- ```18-19.in```
Nakhon Pathom, centered-grouping

- ```20-21.in```
Satun, linear separation

- ```22-27.in```
Nakhon Ratchasima, linear separation

- ```28-33.in```
Nakhon Ratchasima, triangular grouping

- ```34-35.in```
Nakhon Ratchasima, Center Grouping

- ```36-37.in```
Nakhon Ratchasima, Dart-Like shape

- ```38-39.in```
Thailand, Donut-like shape, with simple split like the image below <br>
![thailand Simple Split](testcase_modules/thailand_classification.PNG)

- ```40-41.in```
Thailand, Flower-like shape

- ```42.in```
Thailand, Random Pattern

- ```9999.in```
Thailand, Real Case DF 2013

## Synthesized test case from Original Test Case

- 0000 series (```xx or xxx.in```)

Original input with extremely values

- 1000 series (```1xxx.in```)

replace low and high value with nearly values with mid value

- 2000 series (```2xxx.in```)

replace mid and high value with nearly values with low value

- 3000 series (```3xxx.in```)

replace mid and low value with nearly values with high value

- 9000 series (```9xxx.in```)

all values in the map comes from the real values