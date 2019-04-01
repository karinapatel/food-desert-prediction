# Food Desert Prediction
=============

Prediction and analysis of food deserts from health behavioral data and twitter sentiment in the US. 

### Inspiration

Nutrition and overall access to food is a critical component to well-being and the overall health of an individual. Unfortunately, many regions around the world lack access and ability to consume fresh and quality foods and as a result are suffering to consume the essential components of a healthy diet. Food deserts are the areas across the United States, often low-income, where there is limited access to nutritious and affordable food, especially fruits vegetables, whole grains, and low-fat milk. More specifically, food deserts are census tracts where more than 500 people or over 33 percent of the population in that tract must travel over a mile for fresh groceries. 

With food desert data only being released every 5 years, preventative action could be taken to reverse at-risk regions if we could catch these regions in advanced.

### Goal/Scope

I am predicting food deserts using health behavioral statistics in order to provide more up-to-date predicitons of risk census tracts. I perform additional analysis on the sentiment in social media to try to improve my model and uncover how the prevalence of grocery stores impacts what people talk about on twitter.

 
### Datasets
I utilized health behavioral data from the Population Health Division of the Centers for Disease Control and Prevention. This dataset contains statistics regarding overall health for census tracts across the United States.

I additionally pulled social media twitter data through the Twitter API to analyze patterns of healthy vs. unhealthy consumption. To accomplish this filtered search, I created lists for the following 4 topics and pulled any mention of any of the words in these lists over a span of 1.5 weeks:
    - Common fast food restaurants
    - Top grocery stores/supermarkets
    - Unhealthy foods
    - Healthy foods

### Data Processing


### Food Desert Prediction


### Results


### Interactive Visualizations


==============
### Implementation Details ####



### Necessary Python Packages ####
1. Pandas
2. Numpy
3. NLTK
4. Scikit-Learn
5. requests
6. json
