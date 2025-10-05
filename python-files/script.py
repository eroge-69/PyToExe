#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converted from Jupyter Notebook: notebook.ipynb
Conversion Date: 2025-10-05T15:01:47.125Z
"""

# </div>
# 
# <div style="text-align: center">
#     <h1 style="color:#00589D;padding-bottom:0px">1 Exploratory Data Analysis (EDA) </h1>
#     <h2 style="color:#00589D;padding-bottom:20px">Stats test and theory of sampling </h2>    
# </div>
# 
# <p class="author" style="padding: 0;"><center><b>
#          1st Edition
# 
#          Geostatistics Notes for Practitioners
# 
#          By 
#     Glen Nwaila, Leon Tolmay, Mark Burnett
# </b></center></p>
# <p class="date" style="padding: 0;"><center><b>Copyright 2025</b></center></p>
# 
# ---


# ### Exploratory Data Analysis (EDA):
# 
# Exploratory Data Analysis (EDA) is an essential step in the data analysis process. It involves the initial investigation of data to understand its main characteristics, detect patterns, identify outliers, and form hypotheses. EDA is primarily used to gain insights, generate hypotheses, and guide further analysis.
# 
# Steps for Exploratory Data Analysis:
# 
# 1. Data Collection: Gather the data from reliable sources and ensure it is in a suitable format for analysis.
# 
# 2. Data Cleaning: Handle missing values, outliers, and inconsistencies in the data. This step ensures the data is ready for exploration.
# 
# 3. Summary Statistics: Compute basic summary statistics such as mean, median, standard deviation, etc., to understand the central tendencies and dispersions in the data.
# 
# 4. Data Visualization: Create plots and graphs (histograms, box plots, scatter plots, etc.) to visualize the data's distribution and relationships between variables.
# 
# 5. Identify Patterns: Look for patterns, trends, and relationships between variables in the data. This step helps in generating hypotheses and understanding the data's behavior.
# 
# 6. Outlier Detection: Identify any extreme or unusual observations that might indicate errors or interesting phenomena.
# 
# 7. Correlation Analysis: Examine the correlation between variables to understand their interrelationships.
# 
# 8. Form Hypotheses: Based on the observations and patterns, form preliminary hypotheses about the data.
# 
# 9. Verify Assumptions: Check whether the data meets the assumptions of the subsequent statistical analyses.
# 
# 10. Iterative Process: EDA is often an iterative process, and analysts may revisit some of the earlier steps after gaining insights.
# 
# ### Interpreting P-values:
# 
# * In hypothesis testing, the p-value measures the strength of evidence against the null hypothesis. 
# * A p-value indicates the probability of obtaining the observed results (or more extreme) under the assumption that the null hypothesis is true.
# 
# * A small p-value (typically less than 0.05) suggests strong evidence against the null hypothesis. 
# * It indicates that the observed data is unlikely to occur if the null hypothesis were true, leading to the rejection of the null hypothesis in favor of the alternative hypothesis.
# 
# * A large p-value (typically greater than 0.05) suggests weak evidence against the null hypothesis. 
# * It means that the observed data is likely to occur even if the null hypothesis were true, leading to the failure to reject the null hypothesis.
# 
# ###  Confidence Levels:
# 
# * Confidence levels are associated with confidence intervals, which provide a range of values within which the true population parameter is likely to lie. Common confidence levels are 90%, 95%, and 99%.
# 
# * A 95% confidence level means that if we were to repeat the data sampling process many times and construct a confidence interval each time, we expect about 95% of those intervals to contain the true population parameter.
# 
# ### Probabilities:
# 
# * Probability measures the likelihood of an event occurring. It ranges from 0 to 1, with 0 indicating impossible and 1 indicating certain.
# 
# * Probability is often used to describe the chances of specific outcomes in random events.
# 
# * In statistics, probabilities are employed to model uncertainty and randomness in data and to perform various statistical analyses.
# 
# By employing exploratory data analysis, interpreting p-values, confidence levels, and probabilities, analysts can gain a deeper understanding of the data, make informed decisions, and draw meaningful conclusions from the data analysis process.


# ## Statistical distributions


# * Statistical distributions are mathematical functions that describe the probabilities of different outcomes occurring in a given random experiment or process. There are numerous statistical distributions, but here are some of the most common ones:
# 
# * Normal Distribution (Gaussian Distribution): The most well-known and widely used distribution. It is symmetric, bell-shaped, and characterized by its mean and standard deviation.
# 
# * Uniform Distribution: All outcomes have equal probabilities. It is characterized by a constant probability density function over a specified range.
# 
# * Exponential Distribution: Describes the time between events in a Poisson process. It is often used in survival analysis and reliability studies.
# 
# * Poisson Distribution: Models the number of events that occur in a fixed interval of time or space, given the average rate of occurrence.
# 
# * Binomial Distribution: Represents the number of successes in a fixed number of independent Bernoulli trials, where each trial has the same probability of success.
# 
# * Bernoulli Distribution: A special case of the binomial distribution with a single trial (n=1).
# 
# * Geometric Distribution: Models the number of Bernoulli trials needed until the first success occurs.
# 
# * Negative Binomial Distribution: Represents the number of Bernoulli trials needed until a specified number of successes occur.
# 
# * Chi-Squared Distribution: Arises in the context of the chi-squared test and is often used for hypothesis testing and constructing confidence intervals.
# 
# * Student's t-Distribution: Used for hypothesis testing and constructing confidence intervals when the sample size is small, and the population variance is unknown.
# 
# * F-Distribution: Arises in the context of the F-test and is commonly used in analysis of variance (ANOVA) and regression analysis.
# 
# * Log-Normal Distribution: The logarithm of the random variable follows a normal distribution. Often used for modeling right-skewed data.
# 
# * Weibull Distribution: Used for modeling time-to-event data and survival analysis.
# 
# * Gamma Distribution: Generalizes the exponential distribution and is used in various applications, such as queuing theory and reliability analysis.
# 
# * Pareto Distribution: Commonly used for modeling heavy-tailed distributions and power-law phenomena.
# 
# * Beta Distribution: Defined on the interval [0, 1] and is often used as a prior distribution for probabilities in Bayesian statistics.
# 
# * Logistic Distribution: S-shaped and used in logistic regression and other applications.
# 
# * Cauchy Distribution: Has heavy tails and lacks a defined mean and variance. It is often used as a counterexample in statistics.


import numpy as np  # Fundamental package for numerical computations in Python.
import seaborn as sns  # Statistical data visualization library based on matplotlib.
import matplotlib.pyplot as plt  # Basic plotting library in Python.
import ipywidgets as widgets  # Interactive HTML widgets for Jupyter notebooks and the IPython kernel.
from IPython.display import display  # Display Python objects in rich formats (e.g., images, HTML) within IPython.
import pandas as pd  # Data manipulation and analysis library.
from scipy.stats import norm, lognorm, skew, skewnorm  # Functions from scipy.stats for normal, log-normal distributions, and skew calculations.
from scipy.stats import shapiro, normaltest, kstest  # Statistical tests for normality.
from sklearn.mixture import GaussianMixture  # Gaussian Mixture Model from the scikit-learn library.
from matplotlib_venn import venn3  # Function to create Venn diagrams for three sets.
import random  # Implements pseudo-random number generators for various distributions.
from sklearn.cluster import DBSCAN  # DBSCAN clustering from scikit-learn.
from sklearn import metrics  # Module includes score functions, performance metrics, and pairwise metrics and distance computations.
import os  # Provides a portable way of using operating system dependent functionality (like reading or writing to the filesystem).
import io  # Core tools for working with streams (data flow that can be read or written to).
import logging  # Standard library for logging facilities.
import warnings  # Implements a way to show warning messages to the user.
from tinydb import Query, TinyDB  # TinyDB is a lightweight document oriented database optimized for your happiness.
import sys  # Provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter.
import glob  # Module which finds all the pathnames matching a specified pattern according to the rules used by the Unix shell.
import importlib.util  # Utilities for the import system.

# Add the filter
warnings.filterwarnings("ignore", category=UserWarning)  # Filters out warnings of category UserWarning.


# Dictionary mapping distribution names to their corresponding data generation functions
distribution_functions = {
    'Normal': lambda size: np.random.normal(0, 1, size),
    'Uniform': lambda size: np.random.uniform(-1, 1, size),
    'Exponential': lambda size: np.random.exponential(1, size),
    'Poisson': lambda size: np.random.poisson(1, size),
    'Binomial': lambda size: np.random.binomial(10, 0.5, size),
    'Bernoulli': lambda size: np.random.binomial(1, 0.5, size),
    'Geometric': lambda size: np.random.geometric(0.5, size),
    'Negative Binomial': lambda size: np.random.negative_binomial(5, 0.5, size),
    'Chi-Squared': lambda size: np.random.chisquare(5, size),
    "Student's t": lambda size: np.random.standard_t(5, size),
    'F': lambda size: np.random.f(5, 2, size),
    'Log-Normal': lambda size: np.random.lognormal(0, 1, size),
    'Weibull': lambda size: np.random.weibull(1, size),
    'Gamma': lambda size: np.random.gamma(2, 2, size),
    'Pareto': lambda size: np.random.pareto(2, size) + 1,
    'Beta': lambda size: np.random.beta(2, 5, size),
    'Logistic': lambda size: np.random.logistic(0, 1, size),
    'Cauchy': lambda size: np.random.standard_cauchy(size),
}

# Function to update the plot based on the selected distribution
def update_plot(distribution_type):
    data = distribution_functions[distribution_type](10000)
    sns.histplot(data, kde=True)
    plt.title(f'Distribution: {distribution_type}')
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.show()

# Dropdown widget for selecting the distribution type
distribution_dropdown = widgets.Dropdown(
    options=list(distribution_functions.keys()),
    value='Normal',
    description='Distribution Type:'
)

# Interactive output for the plot
interactive_plot = widgets.interactive(update_plot, distribution_type=distribution_dropdown)

# Display the interactive plot
display(interactive_plot)


# ### Test distribution type


##### First, let's generate synthetic log-normal data using NumPy:

# Generate synthetic log-normal data
lognormal_data = np.random.lognormal(mean=2, sigma=1, size=1000)


# Now, we can use the fit() function from scipy.stats to fit different distributions to this data and determine the best-fitting distribution based on the goodness of fit. We will use the Kolmogorov-Smirnov (KS) test to evaluate the goodness of fit, which measures the maximum vertical distance between the empirical cumulative distribution function (ECDF) of the data and the cumulative distribution function (CDF) of the fitted distribution.
# 
# Here's the code to fit different distributions to the synthetic log-normal data and perform the goodness-of-fit test:


import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# Generate synthetic log-normal data
lognormal_data = np.random.lognormal(mean=2, sigma=1, size=1000)

# List of distribution names to test
distribution_names = ['norm', 'expon', 'gamma', 'lognorm', 'weibull_max']

# Fitting and testing different distributions
best_fit_dist = None
best_ks_statistic = float('inf')
for dist_name in distribution_names:
    # Fit the distribution to the data
    if dist_name == 'norm':
        dist_params = stats.norm.fit(lognormal_data)
    elif dist_name == 'lognorm':
        dist_params = stats.lognorm.fit(lognormal_data)
    elif dist_name == 'gamma':
        dist_params = stats.gamma.fit(lognormal_data)
    elif dist_name == 'weibull_max':
        dist_params = stats.weibull_max.fit(lognormal_data)
    else:
        dist_params = None
    
    if dist_params is not None:
        # Compute the KS test statistic
        ks_statistic = stats.kstest(lognormal_data, dist_name, args=dist_params)[0]
        
        # Check if this distribution has the smallest KS test statistic
        if ks_statistic < best_ks_statistic:
            best_ks_statistic = ks_statistic
            best_fit_dist = dist_name
            best_fit_params = dist_params

# Plot the histogram and the fitted density curve for the best-fitting distribution
plt.figure(figsize=(8, 6))
sns.histplot(lognormal_data, kde=True, label='Data', color='blue')
x = np.linspace(np.min(lognormal_data), np.max(lognormal_data), 1000)
if best_fit_dist is not None:
    best_fit_distribution = getattr(stats, best_fit_dist)
    fitted_pdf = best_fit_distribution.pdf(x, *best_fit_params)
    plt.plot(x, fitted_pdf, label=best_fit_dist, color='red')
plt.title(f'Best-Fitting Distribution: {best_fit_dist}\nKS Statistic: {best_ks_statistic:.4f}')
plt.xlabel('Value')
plt.ylabel('Density')
plt.legend()
plt.show()


# generate synthetic data
np.random.seed(0)
X = np.concatenate([np.random.normal(0, 1, size=50),                    np.random.normal(5, 1, size=50)])

# define function to fit and plot GMM
def plot_gmm(num_components):
    # fit GMM
    gmm = GaussianMixture(n_components=num_components, covariance_type='full')
    gmm.fit(X.reshape(-1, 1))
    x = np.linspace(-5, 10, 100)
    logprob = gmm.score_samples(x.reshape(-1, 1))
    pdf = np.exp(logprob)
    # plot data and GMM
    plt.figure(figsize=(10, 5))
    plt.hist(X, bins=20, density=True, alpha=0.5, label='data')
    plt.plot(x, pdf, '-k', label='GMM')
    for i in range(num_components):
        mu, std = gmm.means_[i][0], np.sqrt(gmm.covariances_[i][0][0])
        plt.plot(x, norm.pdf(x, mu, std), '--r', label='component {}'.format(i+1))
    plt.xlabel('x')
    plt.ylabel('p(x)')
    plt.title('Number of components = {}'.format(num_components))
    plt.legend()
    plt.show()

# create interactive plot
from ipywidgets import interact
interact(plot_gmm, num_components=[1, 2, 3, 4, 5, 6, 7, 8]);


import numpy as np
import matplotlib.pyplot as plt

# Generate data for unimodal, bimodal, and multimodal distributions
np.random.seed(0)
unimodal = np.random.normal(0, 1, size=1000)
bimodal = np.concatenate([np.random.normal(-1, 1, size=500), np.random.normal(1, 1, size=500)])
multimodal = np.concatenate([np.random.normal(-2, 1, size=250), np.random.normal(-1, 1, size=250),
                             np.random.normal(1, 1, size=250), np.random.normal(2, 1, size=250)])

# Create a figure with three subplots
# Create a figure with three subplots
fig, ax = plt.subplots(1, 3, figsize=(12, 4))

# Plot the data in histograms
hist1, bins1, lines1 = ax[0].hist(unimodal, bins=30, alpha=0.5, color='blue', label='Unimodal')
hist2, bins2, lines2 = ax[1].hist(bimodal, bins=30, alpha=0.5, color='green', label='Bimodal')
hist3, bins3, lines3 = ax[2].hist(multimodal, bins=30, alpha=0.5, color='red', label='Multimodal')

# Show the legend
ax[0].legend()
ax[1].legend()
ax[2].legend()

# Label the x-axis
#ax[0].set_xlabel('X')

plt.show()


# Generate synthetic data with negative skew
mean, std, skew = 3, 1, 30
positive_skew = skewnorm.rvs(skew, mean, std, size=1000)
mean, std, skew = 5, 1, 0
normal_skew = skewnorm.rvs(skew, mean, std, size=1000)
mean, std, skew = 5, 1, -5
negative_skew = skewnorm.rvs(skew, mean, std, size=1000)

# Create a figure with three subplots
fig, ax = plt.subplots(1, 3, figsize=(12, 4))

# Plot the data in histograms
hist1, bins1, lines1 = ax[0].hist(negative_skew, bins=30, alpha=0.5, color='blue', label='Negative Skew')
hist2, bins2, lines2 = ax[1].hist(normal_skew, bins=30, alpha=0.5, color='green', label='Normal Skew')
hist3, bins3, lines3 = ax[2].hist(positive_skew, bins=30, alpha=0.5, color='red', label='Positive Skew')

# Show the legend
ax[0].legend()

# Label the x-axis
ax[0].set_xlabel('X')

# Label the y-axis
ax[0].set_ylabel('Frequency')

# Show the plot
plt.show()


# Generate synthetic data with highly positive skew
mean, std, skew = 5, 1, -5
positive_skew = skewnorm.rvs(skew, mean, std, size=1000)

# Create a figure with one subplot
fig, ax = plt.subplots(figsize=(6, 4))

# Plot the data in a histogram
hist, bins, lines = ax.hist(positive_skew, bins=30, alpha=0.5)

# Label the axes and show the plot
ax.set_xlabel('X')
ax.set_ylabel('Frequency')
ax.set_title('Highly Positively Skewed Distribution')
ax.grid(True)
plt.show()


# To check for the type of distribution in a given dataset, you can use various statistical tests and visualizations. Some common approaches include:
# 
# Visual inspection of histograms and box plots: These plots can give you a rough idea of the shape of the distribution. For example, a histogram with a long tail on one side is likely to be skewed, while a histogram with a symmetrical shape is likely to be approximately normal.
# 
# Skewness and kurtosis: These statistical measures describe the degree of asymmetry and peakedness, respectively, of a distribution. A distribution with a large positive skewness (skewed to the right) is likely to be positively skewed, while a distribution with a large negative skewness (skewed to the left) is likely to be negatively skewed. Similarly, a distribution with a large kurtosis (peaked) is likely to be leptokurtic (more peaked than a normal distribution), while a distribution with a small kurtosis (flat) is likely to be platykurtic (less peaked than a normal distribution).
# 
# Statistical tests: There are various statistical tests that can be used to formally test the normality of a distribution. Some common tests include the Anderson-Darling test, the Shapiro-Wilk test, and the Jarque-Bera test. These tests typically return a p-value, which can be used to determine the likelihood that the distribution is normal (p-value > 0.05 indicates that the distribution is likely to be normal).
# 
# It's worth noting that no single method is foolproof, and it's often necessary to use a combination of these approaches to get a good idea of the shape of the distribution. Additionally, it's important to keep in mind that some distributions, such as the t-distribution, have properties that are intermediate between the normal and skewed distributions.


# Generate synthetic data with normal distribution
mean, std, skew = 5, 1, -5

data = skewnorm.rvs(skew, mean, std, size=1000)

# Perform the D'Agostino-Pearson test
statistic, pvalue = normaltest(data)

# Check the p-value
if pvalue < 0.05:
    print('The data does not follow a normal distribution (p-value = {:.3f})'.format(pvalue))
else:
    print('The data follows a normal distribution (p-value = {:.3f})'.format(pvalue))


# ### Let's try smething new on multivariate statistics


np.random.seed(42)

# Create a normal distributed feature
feature_1 = np.random.normal(loc=50, scale=10, size=1000)

# Create a lognormal distributed feature
feature_2 = np.random.lognormal(mean=0, sigma=1, size=1000)

# Create a skewed normal distributed feature using skewnorm
a = 5  # Skewness parameter
feature_3 = skewnorm.rvs(a, loc=50, scale=10, size=1000)

# Create another normal distributed feature
feature_4 = np.random.normal(loc=50, scale=10, size=1000)

# Create another lognormal distributed feature
feature_5 = np.random.lognormal(mean=0, sigma=1, size=1000)

# Create another skewed normal distributed feature using skewnorm
feature_6 = skewnorm.rvs(a, loc=50, scale=10, size=1000)

# Create a DataFrame
data = {'feature_1': feature_1, 'feature_2': feature_2, 'feature_3': feature_3, 'feature_4': feature_4, 'feature_5': feature_5, 'feature_6': feature_6}
df = pd.DataFrame(data)

# Perform exploratory data analysis
sns.pairplot(df)
plt.show()


# Check normality of features
print("Shapiro Test Results:")
for col in df.columns:
    stat, p = shapiro(df[col])
    print(col, ": statistic=%.3f, p=%.3f" % (stat, p))




print("\nNormality Test Results:")
for col in df.columns:
    stat, p = normaltest(df[col])
    print(col, ": statistic=%.3f, p=%.3f" % (stat, p))



print("\nKolmogorov-Smirnov Test Results:")
for col in df.columns:
    stat, p = kstest(df[col], 'norm')
    print(col, ": statistic=%.3f, p=%.3f" % (stat, p))

import matplotlib.pyplot as plt
import scipy.stats as stats

# Histograms
df.hist(bins=20, figsize=(10,8))
plt.tight_layout()
plt.show()





# Boxplots
df.plot(kind='box', subplots=True, layout=(2,3), sharex=False, sharey=False, figsize=(10,8))
plt.show()




# Summary statistics
print(df.describe())

# Check for outliers: You can use the interquartile range (IQR) method to identify any outliers. This method is based on the difference between the first and third quartiles (75th and 25th percentiles) of a distribution. Any data points that fall outside of the range of 1.5 times the IQR are considered outliers.


# Calculate the IQR for each feature
Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3 - Q1

# Identify any outliers
outliers = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]

# Print the number of outliers for each feature
print(outliers.count())


corr_matrix = df.corr()
print(corr_matrix)

import seaborn as sns
import matplotlib.pyplot as plt

sns.heatmap(corr_matrix, annot=True)
plt.show()


from scipy import stats
z = np.abs(stats.zscore(df))

# identify and print outlier rows
outliers = np.where(z > 3)
print(df.iloc[outliers])

# create DBSCAN instance
db = DBSCAN(eps=3, min_samples=4).fit(df)

# predict clusters
labels = db.labels_

# identify and print outlier rows
outliers = np.where(labels == -1)
print(df.iloc[outliers])


# 
# * Probabilities in the context of statistics and probability theory represent the likelihood of an event occurring. It is a numerical value between 0 and 1, where 0 indicates an impossible event, and 1 represents a certain event. Probabilities are essential for making predictions, decision-making under uncertainty, and analyzing random phenomena.
# 
# There are three common types of probabilities:
# 
# * Marginal Probability:
# The probability of a single event occurring, without considering any other events. It deals with individual probabilities in isolation.
# 
# * Conditional Probability:
# The probability of an event occurring given that another event has already occurred. It considers the relationship between two events.
# 
# *  Joint Probability:
# The probability of two or more events occurring simultaneously.
# 
# Let's demonstrate each type of probability with code examples using synthetic data in Python.
# 
# We will first generate synthetic data to represent a simple scenario of rolling two dice, and then we'll compute probabilities based on this data.


# Generate synthetic data for two dice rolls
num_trials = 10000
dice1_rolls = [random.randint(1, 6) for _ in range(num_trials)]
dice2_rolls = [random.randint(1, 6) for _ in range(num_trials)]

# Function to compute probability of an event
def compute_probability(event_occurrences, total_trials):
    return event_occurrences / total_trials

# Function to compute joint probability of two events
def compute_joint_probability(event1_occurrences, event2_occurrences, total_trials):
    return (event1_occurrences + event2_occurrences) / total_trials

# Marginal Probability
def compute_marginal_probability(roll_results, target_value):
    occurrences = roll_results.count(target_value)
    return compute_probability(occurrences, len(roll_results))

# Conditional Probability
def compute_conditional_probability(given_results, target_value):
    occurrences_given = given_results.count(target_value)
    return compute_probability(occurrences_given, len(given_results))

# Joint Probability
def compute_joint_probability_two_dice(roll_results1, roll_results2, target_value1, target_value2):
    occurrences1 = roll_results1.count(target_value1)
    occurrences2 = roll_results2.count(target_value2)
    return compute_joint_probability(occurrences1, occurrences2, len(roll_results1))

# Test the probabilities with synthetic data
target_value1 = 3
target_value2 = 4

marginal_probability_dice1 = compute_marginal_probability(dice1_rolls, target_value1)
marginal_probability_dice2 = compute_marginal_probability(dice2_rolls, target_value2)

joint_probability_both_3_and_4 = compute_joint_probability_two_dice(dice1_rolls, dice2_rolls, target_value1, target_value2)

conditional_probability_dice2_given_dice1_3 = compute_conditional_probability(dice1_rolls, target_value1)

# Print the results
print(f"Marginal Probability of getting {target_value1} on Dice 1: {marginal_probability_dice1:.4f}")
print(f"Marginal Probability of getting {target_value2} on Dice 2: {marginal_probability_dice2:.4f}")
print(f"Joint Probability of getting {target_value1} on Dice 1 and {target_value2} on Dice 2: {joint_probability_both_3_and_4:.4f}")
print(f"Conditional Probability of getting {target_value2} on Dice 2 given Dice 1 is {target_value1}: {conditional_probability_dice2_given_dice1_3:.4f}")

# Interpretation:
# 
# * Marginal Probability of getting 3 on Dice 1:
# This represents the probability of rolling a 3 on the first die without considering the second die's outcome.
# 
# *  Marginal Probability of getting 4 on Dice 2:
# This represents the probability of rolling a 4 on the second die without considering the first die's outcome.
# 
# *  Joint Probability of getting 3 on Dice 1 and 4 on Dice 2:
# This represents the probability of rolling a 3 on the first die and a 4 on the second die in the same trial.
# 
# *  Conditional Probability of getting 4 on Dice 2 given Dice 1 is 3:
# This represents the probability of rolling a 4 on the second die given that the first die shows a 3.


# * Marginal Probability:
# Marginal probability refers to the probability of a single event occurring, without taking into account any other events. It represents the likelihood of observing a particular outcome in isolation.
# For a discrete random variable X taking values {x1, x2, ..., xn}, the marginal probability of observing a specific value xi is given by the ratio of the number of occurrences of xi to the total number of observations (trials):
# 
# Marginal Probability of X = xi = P(X = xi) = Number of occurrences of xi / Total number of trials
# In our example, for Dice 1, the marginal probability of getting a particular value (e.g., 3) is computed by dividing the number of times 3 occurs on Dice 1 by the total number of trials.
# 
# * Conditional Probability:
# Conditional probability refers to the probability of an event occurring given that another event has already occurred. It measures the likelihood of one event happening under the condition that we know some information about the outcome of another event.
# For two events A and B, the conditional probability of A given B is calculated as follows:
# 
# Conditional Probability of A given B = P(A | B) = P(A and B) / P(B)
# where P(A and B) is the joint probability of both events A and B occurring together, and P(B) is the probability of event B occurring.
# 
# In our example, we compute the conditional probability of getting a particular value (e.g., 4) on Dice 2, given that we already know Dice 1 shows a specific value (e.g., 3).
# 
# * Joint Probability:
# Joint probability refers to the probability of two or more events occurring simultaneously. It represents the likelihood of observing the intersection of multiple events.
# For two events A and B, the joint probability of both A and B occurring is calculated as follows:
# 
# Joint Probability of A and B = P(A and B) = Number of occurrences of (A and B) / Total number of trials
# In our example, we compute the joint probability of getting a specific value on Dice 1 (e.g., 3) and a particular value on Dice 2 (e.g., 4) in the same trial.


# pip install matplotlib-venn


# Sample data for mineral occurrences
gold_occurrences = 50
silver_occurrences = 30
copper_occurrences = 40
gold_silver_occurrences = 15
gold_copper_occurrences = 20
silver_copper_occurrences = 10
gold_silver_copper_occurrences = 5

# Total occurrences in the region
total_occurrences = gold_occurrences + silver_occurrences + copper_occurrences - gold_silver_occurrences - gold_copper_occurrences - silver_copper_occurrences + gold_silver_copper_occurrences

# Marginal probabilities
marginal_probability_gold = gold_occurrences / total_occurrences
marginal_probability_silver = silver_occurrences / total_occurrences
marginal_probability_copper = copper_occurrences / total_occurrences

# Conditional probabilities
conditional_probability_silver_given_gold = gold_silver_occurrences / gold_occurrences
conditional_probability_copper_given_gold = gold_copper_occurrences / gold_occurrences

# Joint probability
joint_probability_gold_silver = gold_silver_occurrences / total_occurrences
joint_probability_gold_copper = gold_copper_occurrences / total_occurrences
joint_probability_silver_copper = silver_copper_occurrences / total_occurrences
joint_probability_gold_silver_copper = gold_silver_copper_occurrences / total_occurrences

# Draw Venn diagram for marginal probability
plt.figure(figsize=(6, 6))
venn3(subsets=(gold_occurrences, silver_occurrences, gold_silver_occurrences, copper_occurrences, gold_copper_occurrences, silver_copper_occurrences, gold_silver_copper_occurrences), set_labels=('Gold', 'Silver', 'Copper'))
plt.title("Venn Diagram for Marginal Probability")
plt.show()

# Draw Venn diagram for conditional probability
plt.figure(figsize=(6, 6))
venn3(subsets=(gold_occurrences, silver_occurrences, gold_silver_occurrences, copper_occurrences, gold_copper_occurrences, silver_copper_occurrences, gold_silver_copper_occurrences), set_labels=('Gold', 'Silver', 'Copper'))
plt.title("Venn Diagram for Conditional Probability (Gold Given Silver)")
plt.show()

plt.figure(figsize=(6, 6))
venn3(subsets=(gold_occurrences, silver_occurrences, gold_silver_occurrences, copper_occurrences, gold_copper_occurrences, silver_copper_occurrences, gold_silver_copper_occurrences), set_labels=('Gold', 'Silver', 'Copper'))
plt.title("Venn Diagram for Conditional Probability (Gold Given Copper)")
plt.show()

# Draw Venn diagram for joint probability
plt.figure(figsize=(6, 6))
venn3(subsets=(gold_occurrences, silver_occurrences, gold_silver_occurrences, copper_occurrences, gold_copper_occurrences, silver_copper_occurrences, gold_silver_copper_occurrences), set_labels=('Gold', 'Silver', 'Copper'))
plt.title("Venn Diagram for Joint Probability")
plt.show()


# Generating synthetic data for cobalt grades using log-normal distribution
np.random.seed(42)
num_samples = 1000
mu, sigma = 0, 0.5
cobalt_grades = np.random.lognormal(mu, sigma, num_samples)

# Defining log-normal PDF function for cobalt grades
def lognormal_pdf(x, mu, sigma):
    return 1 / (x * sigma * np.sqrt(2 * np.pi)) * np.exp(-((np.log(x) - mu) ** 2) / (2 * sigma ** 2))

# Calculate the unconditional probability using the PDF
def unconditional_probability(pdf_func, threshold):
    x_subset = x_values[pdf_func > threshold]
    return np.trapz(pdf_func[pdf_func > threshold], x_subset)

# Joint probability (e.g., probability of cobalt grade > 0.9 and grade < 2)
def joint_probability(pdf_func, lower_threshold, upper_threshold):
    x_subset = x_values[(pdf_func > lower_threshold) & (pdf_func < upper_threshold)]
    return np.trapz(pdf_func[(pdf_func > lower_threshold) & (pdf_func < upper_threshold)], x_subset)

# Marginal conditional probability (e.g., probability of cobalt grade > 0.9 given grade > 0.9)
def marginal_conditional_probability(pdf_func, threshold_1, threshold_2):
    return joint_probability(pdf_func, threshold_1, threshold_2) / unconditional_probability(pdf_func, threshold_2)

# Calculate the PDF values for cobalt grades
x_values = np.linspace(0.001, 5, 1000)  # Define a range for PDF evaluation
pdf_values = lognormal_pdf(x_values, mu, sigma)

# Unconditional probability
threshold_low_unconditional = 0.9
prob_unconditional = unconditional_probability(pdf_values, threshold_low_unconditional)

# Joint probability
threshold_low_joint = 0.7
threshold_high_joint = 1.2
prob_joint = joint_probability(pdf_values, threshold_low_joint, threshold_high_joint)

# Marginal conditional probability
threshold_conditional = 0.71
prob_conditional = marginal_conditional_probability(pdf_values, threshold_low_joint, threshold_conditional)

# Plot the log-normal distribution PDF
plt.figure(figsize=(8, 6))
plt.plot(x_values, pdf_values)
plt.fill_between(x_values, pdf_values, where=(x_values > threshold_low_joint) & (x_values < threshold_high_joint), color='gray', alpha=0.5)
plt.xlabel('Cobalt Grades')
plt.ylabel('Probability Density')
plt.title('Log-Normal Distribution of Cobalt Grades')
plt.show()

# Display results
print(f"Unconditional Probability (cobalt grade > {threshold_low_unconditional}): {prob_unconditional:.2f}")
print(f"Joint Probability (cobalt grade > {threshold_low_joint} and grade < {threshold_high_joint}): {prob_joint:.2f}")
print(f"Marginal Conditional Probability (cobalt grade > {threshold_low_joint} given grade > {threshold_conditional}): {prob_conditional:.2f}")


# ### If you are a geochemist - you may also want to plot data with reference compositinal samples



current_path = os.getcwd()
current_path

# Define the directory where the reference composition datasets are stored
directory = current_path+"\\input_data\\data\\geochem\\refcomp"
file_pattern = os.path.join(directory, "*.csv")

# Function to load reference datasets into a dictionary
def load_reference_compositions(pattern):
    reference_compositions = {}
    for file_path in glob.glob(pattern):
        model_name = os.path.basename(file_path).split('.')[0]  # Extract the model name from the file name
        print(model_name)
        reference_compositions[model_name] = pd.read_csv(file_path)  # Add delimiter if not comma
    return reference_compositions

# Load all reference datasets
ref_comps = load_reference_compositions(file_pattern)

#The file names below represent reference compositions



# Function to select a reference dataset and extract values for given elements
def get_reference_values(ref_comps, dataset_name, elements):
    if dataset_name not in ref_comps:

        raise ValueError(f"Dataset {dataset_name} not found.")
    df = ref_comps[dataset_name]
    df = df.set_index('var')  # Assuming 'var' column contains the element names
    ref_values = df.loc[elements]['value'].to_dict()
    # Convert values to numeric, stripping units if present
    ref_values = {el: pd.to_numeric(val.replace(' ppm', '').replace('%', '')) for el, val in ref_values.items() if pd.notnull(val)}
    return ref_values

# ## Load your dataset 1 below by changing file name REE.xlsx


dataset_1 = pd.read_excel(current_path+"\\input_data\\REE.xlsx", sheet_name="REE", skiprows=None)
dataset_1

dataset_1.columns

# ## Select the elements you want to normalise and the normalising dataset


# List of elements you're interested in
my_elements = ['La', 'Ce', 'Nd', 'Sm', 'Eu', 'Gd', 'Dy', 'Er', 'Yb', 'Lu']

# Select the reference dataset name
chosen_dataset_name = "CH_PalmeONeill2014"
# Get the reference values for the selected elements
reference_values = get_reference_values(ref_comps, chosen_dataset_name, my_elements)


# Normalize your dataset by reference values (this is a simple division, replace with your actual normalization)
normalized_data = dataset_1.copy()
for el in reference_values:
    normalized_data[el] = normalized_data[el] / reference_values[el]

# Set up the plot
fig, ax = plt.subplots(figsize=(8, 6))

# Get unique rock types
rock_types = dataset_1['ROCK NAME'].unique()

# Define marker styles for each rock type for better visualization
markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', '|', '_']

# Color map for plotting; using a simple categorical colormap
colors = plt.colormaps['tab10'](np.linspace(0, 1, len(rock_types)))

# Log scale for y-axis
ax.set_yscale('log')

# Set limits for the y-axis
ax.set_ylim([1e-1, 1e3]) #change the values to match your data log scale

# Iterate over each rock type and plot
for idx, rock_type in enumerate(rock_types):
    subset = normalized_data[normalized_data['ROCK NAME'] == rock_type]
    elements = ['La', 'Ce', 'Nd', 'Sm', 'Eu', 'Gd', 'Dy', 'Er', 'Yb', 'Lu']
    ax.plot(elements, subset[elements].T, marker=markers[idx % len(markers)], color=colors[idx], label=rock_type)

# Plot a dashed horizontal line at y=1 across the entire x-axis range
ax.hlines(y=1, xmin=0, xmax=len(my_elements)-1, colors='black', linestyles='dashed', label='Chondritic Normalization')

# Enhancements
ax.set_xlabel('Element', fontsize=12)
ax.set_ylabel('X/X$_{Chondrite}$', fontsize=12)
ax.set_title('REE Concentrations Normalized to Chondritic Values', fontsize=10)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Legend enhancements - increased bbox_to_anchor's negative y-offset for better placement
legend = ax.legend(title='Rock Type', fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, ncol=5)

# Tight layout adjustments - may need to tweak the pad parameter based on your figure size
plt.tight_layout(pad=2.0)

# Save the figure as high res png and pdf
fig.savefig('normalized_ree_plot.png', dpi=600, bbox_inches='tight')
fig.savefig('normalized_ree_plot.pdf', bbox_inches='tight')

# Show the plot
plt.show()

# Show the plot
plt.show()


## Load your dataset 2 below by changing file name Spider.xlsx

dataset_2 = pd.read_excel(current_path+"\\input_data\\Spider.xlsx", sheet_name="Trace elements", skiprows=None)
dataset_2

dataset_2.columns

# List of elements you're interested in
my_elements_dataset_2 = ['Rb', 'Ba', 'Th', 'Nb', 'Ta', 'U', 'La', 'Ce', 'Pb', 'Nd',
       'Sr', 'Sm', 'Zr', 'Hf', 'Y', 'Yb']

# Select the reference dataset name
chosen_dataset_name = "CH_PalmeONeill2014"
# Get the reference values for the selected elements
reference_values = get_reference_values(ref_comps, chosen_dataset_name, my_elements_dataset_2)


# Normalize your dataset by reference values (this is a simple division, replace with your actual normalization)
normalized_data = dataset_2.copy() #tgis is where you use your own database
for el in reference_values:
    normalized_data[el] = normalized_data[el] / reference_values[el]

# Set up the plot
fig, ax = plt.subplots(figsize=(8, 6))

# Get unique rock types
rock_types = dataset_2['CITATIONS'].unique()

# Define marker styles for each rock type for better visualization
markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', '|', '_']

# Color map for plotting; using a simple categorical colormap
colors = plt.colormaps['tab10'](np.linspace(0, 1, len(rock_types)))

# Log scale for y-axis
ax.set_yscale('log')

# Set limits for the y-axis
ax.set_ylim([1e-1, 1e3]) #change the values to match your data log scale

# Iterate over each rock type and plot
for idx, rock_type in enumerate(rock_types):
    subset = normalized_data[normalized_data['CITATIONS'] == rock_type]
    elements = my_elements_dataset_2
    ax.plot(elements, subset[elements].T, marker=markers[idx % len(markers)], color=colors[idx], label=rock_type)

# Plot a dashed horizontal line at y=1 across the entire x-axis range
ax.hlines(y=1, xmin=0, xmax=len(my_elements_dataset_2)-1, colors='black', linestyles='dashed', label='Chondritic Normalization')

# Enhancements
ax.set_xlabel('Element', fontsize=12)
ax.set_ylabel('X/X$_{Chondrite}$', fontsize=12)
ax.set_title('REE Concentrations Normalized to Chondritic Values', fontsize=10)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Legend enhancements - increased bbox_to_anchor's negative y-offset for better placement
legend = ax.legend(title='Rock Type', fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, ncol=5)

# Tight layout adjustments - may need to tweak the pad parameter based on your figure size
plt.tight_layout(pad=2.0)

# Save the figure as high res png and pdf
fig.savefig('normalized_trace_plot.png', dpi=600, bbox_inches='tight')
fig.savefig('normalized_trace_plot.pdf', bbox_inches='tight')

# Show the plot
plt.show()

# Show the plot
plt.show()


# Setup for dataset_1
my_elements = ['La', 'Ce', 'Nd', 'Sm', 'Eu', 'Gd', 'Dy', 'Er', 'Yb', 'Lu']
chosen_dataset_name = "CH_PalmeONeill2014"
reference_values_1 = get_reference_values(ref_comps, chosen_dataset_name, my_elements)

# Normalize dataset_1
normalized_data_1 = dataset_1.copy()
for el in reference_values_1:
    normalized_data_1[el] = normalized_data_1[el] / reference_values_1[el]

# Setup for dataset_2
my_elements_dataset_2 = ['Rb', 'Ba', 'Th', 'Nb', 'Ta', 'U', 'La', 'Ce', 'Pb', 'Nd', 'Sr', 'Sm', 'Zr', 'Hf', 'Y', 'Yb']
reference_values_2 = get_reference_values(ref_comps, chosen_dataset_name, my_elements_dataset_2)

# Normalize dataset_2
normalized_data_2 = dataset_2.copy()
for el in reference_values_2:
    normalized_data_2[el] = normalized_data_2[el] / reference_values_2[el]

# Create a figure and two subplots, side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# ------------- Plot for dataset_1 -------------
# Plot each rock type in dataset_1
for rock_type in dataset_1['ROCK NAME'].unique():
    subset = normalized_data_1[normalized_data_1['ROCK NAME'] == rock_type]
    ax1.plot(my_elements, subset[my_elements].T, marker='o', linestyle='-', label=rock_type)

# Set log scale, labels, title, and grid for the left plot
ax1.set_yscale('log')
ax1.set_ylim([1e-1, 1e3])
ax1.set_title('(a) REE Concentrations Normalized to CH Palme & O’Neill 2014')
ax1.set_xlabel('Element')
ax1.set_ylabel('X/X$_{Chondrite}$')
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.legend(title='Rock Type', loc='lower left', fancybox=True, ncol=4)

# ------------- Plot for dataset_2 -------------
# Plot each rock type in dataset_2
for rock_type in dataset_2['CITATIONS'].unique():
    subset = normalized_data_2[normalized_data_2['CITATIONS'] == rock_type]
    ax2.plot(my_elements_dataset_2, subset[my_elements_dataset_2].T, marker='s', linestyle='-', label=rock_type)

# Set log scale, labels, title, and grid for the right plot
ax2.set_yscale('log')
ax2.set_ylim([1e-1, 1e3])
ax2.set_title('(b) Trace Element Normalization to CH Palme & O’Neill 2014')
ax2.set_xlabel('Element')
ax2.set_ylabel('X/X$_{Chondrite}$')
ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
ax2.legend(title='Citation Type', loc='lower left', fancybox=True, ncol=4)

# Adjust layout to avoid overlap and ensure all components fit
plt.tight_layout(pad=3.0)

# Save the combined figure as high-res PNG and PDF
fig.savefig('combined_normalized_plots.png', dpi=600, bbox_inches='tight')
fig.savefig('combined_normalized_plots.pdf', bbox_inches='tight')

# Display the plot
plt.show()


import ternary
import matplotlib.pyplot as plt

def plot_ternary_diagram():
    # Setup the figure and ternary axes
    figure, tax = ternary.figure(scale=100)
    tax.set_title("Ternary Diagram for Igneous Rocks", fontsize=10, fontdict={'family': 'Arial'}, pad=20)

    # Adjust font through matplotlib's rcParams
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 10


    # Set labels with custom fontdict and LaTeX subscripts
    font = {'family': 'Arial', 'size': 10}
    tax.left_corner_label(r"SiO$_2$", fontdict=font, offset=0.12)
    tax.right_corner_label("Fe+Mg", fontdict=font, offset=0.12)
    tax.top_corner_label(r"Al$_2$O$_3$", fontdict=font, offset=0.2)

    # Gridlines and scale ticks
    tax.gridlines(multiple=10, color="blue")
    tax.ticks(axis='lbr', linewidth=1, multiple=10, tick_formats="%.1f")

    # Example data points
    granite = [70, 10, 20]
    basalt = [50, 25, 25]
    gabbro = [48, 30, 22]

    # Add points with different colors
    tax.scatter([granite], marker='o', color='red', label="Granite")
    tax.scatter([basalt], marker='o', color='green', label="Basalt")
    tax.scatter([gabbro], marker='o', color='blue', label="Gabbro")

    # Draw boundary and gridlines
    tax.boundary(linewidth=2.0)

    # Legend with fancy box
    tax.legend(frameon=True, fancybox=True)

    # Remove default matplotlib axes
    tax.clear_matplotlib_ticks()
    tax.get_axes().axis('off')

    # Show the plot
    plt.show()

# Call the function to plot
plot_ternary_diagram()


import pandas as pd
import numpy as np
import os

# Function to generate synthetic data
def create_dummy_data(elements, num_samples=10):
    data = {el: np.random.normal(20, 100, num_samples) for el in elements}
    return pd.DataFrame(data)

# Elements and files setup
elements = ['MgO', 'SiO2', 'FeOt', 'Al2O3', 'CaO', 'TiO2', 'P2O5']
files = ['wits_shale.csv', 'german_shale.csv', 'gabon_shale.csv', 'australia_shale.csv', 'london_shale.csv']
dataset_names = ['wits_shale', 'german_shale', 'gabon_shale', 'australia_shale', 'london_shale']

# Generate and save data
for file_name in files:
    df = create_dummy_data(elements)
    df.to_csv(file_name)


def makeHarker(fileList, elementsList, datasetNames, outputFileName):
    import matplotlib.pyplot as plt

    datasetsDict = {}

    # Import data files
    for i, f in enumerate(fileList):
        if os.path.exists(f):
            d = pd.read_csv(f, index_col=0)
            dataName = datasetNames[i]

            for e in elementsList:
                if e in d.columns:
                    datasetsDict[(dataName, e)] = d[e].tolist()
                else:
                    print(f"Element {e} not found in {f}.")
        else:
            print(f"File {f} not found.")

    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 8

    fig, axs = plt.subplots(3, 2, figsize=(6, 8))
    sub = axs.flatten()

    labels = [r'SiO$_2$ (wt%)', r'FeO$_T$ (wt%)', r'Al$_2$O$_3$ (wt%)', 'CaO (wt%)', r'TiO$_2$ (wt%)',
              r'P$_2$O$_5$ (wt%)']
    symbolsDict = {'wits_shale': '^', 'german_shale': 'v', 'gabon_shale': 'p', 'australia_shale': 'D', 'london_shale': 'o'}
    coloursDict = {'wits_shale': '#7fc97f', 'german_shale': '#beaed4', 'gabon_shale': '#fdc086',
                   'australia_shale': '#386cb0', 'london_shale': '#f0027f'}
    titles = ['a)', 'b)', 'c)', 'd)', 'e)', 'f)']

    for s, e in enumerate(elementsList[1:]):
        for n in datasetNames:
            key_mgo = (n, 'MgO')
            key_elem = (n, e)
            if key_mgo in datasetsDict and key_elem in datasetsDict:
                sub[s].plot(datasetsDict[key_mgo], datasetsDict[key_elem], symbolsDict[n],
                            markerfacecolor=coloursDict[n], markeredgecolor='none', markersize=4, label=n)
            else:
                print(f"Data for {n} or element {e} missing.")

        sub[s].set_xlabel('MgO (wt%)')
        sub[s].set_ylabel(labels[s])
        sub[s].legend(numpoints=1, fontsize=6)
        sub[s].set_title(titles[s], loc='left')

    plt.tight_layout()
    plt.savefig(outputFileName + '.png', dpi=300, bbox_inches='tight', pad_inches=0.25)
    plt.show()

makeHarker(files, elements, dataset_names, 'Figure_12')