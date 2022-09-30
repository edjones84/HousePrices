![Screenshot 2022-09-30 at 10 07 24](https://user-images.githubusercontent.com/78102381/193235557-2b2f44f4-7fbf-432a-b51b-56714d0d4e2b.png)


This repository contains a number of very useful functions/classes/code to help predict the future of the housing market
. The following functionality is present:
- api class to retrieve the last 20 years of house price data for both the local area and your country (https://www.landregistry.data.gov.uk/data/ukhpi/region). This house price data consists of both the House Price Index<sup>1</sup> and the average property price
- multithread class that allows for multithreading of api calls to the land registry
- forecaster class that utilises neural prophet - making predictions 5 years in the future - "NeuralProphet bridges the gap between traditional time-series models and deep learning methods. It's based on PyTorch and can be installed using pip." https://neuralprophet.com/html/index.html
- a locally hosted web interface via Flask to enter your postcode and view the data


<sup>1</sup>  A house price index (HPI) measures the price changes of residential housing as a percentage change from some specific start date (which has an HPI of 100). Methodologies commonly used to calculate an HPI are hedonic regression (HR), simple moving average (SMA), and repeat-sales regression (RSR).


### Setup/ Running
1. Install requirements: 
```
pip install -r requirements
```

2. Run flask app:
```
python -m flask run 
```

3. Go to your local host: http://127.0.0.1:5000/

4. Enter your postcode

5. You will then be prompted with what chart you would like to see (see image above). When you click either of these 
neural prophet is then "deployed". This data is then cached for future viewing


