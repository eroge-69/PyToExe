# ClickBank Affiliate Marketing Program
# This program automates some basic tasks for ClickBank affiliate marketing.
# It generates promotional content, analyzes performance data, and provides optimization advice.

import random

# Function to generate promotional content

def generate_content(product_name):
    prompts = [
        f"Check out {product_name}, it's amazing!",
        f"Don't miss out on {product_name}, grab it now!",
        f"Discover the benefits of {product_name} today!"
    ]
    return random.choice(prompts)

# Function to analyze past performance (mock data)

def analyze_performance(data):
    total_sales = sum(data['sales'])
    total_clicks = sum(data['clicks'])
    conversion_rate = total_sales / total_clicks * 100 if total_clicks > 0 else 0
    return {
        'total_sales': total_sales,
        'conversion_rate': conversion_rate
    }

# Function to optimize campaigns based on analysis

def optimize_campaign(performance_data):
    if performance_data['conversion_rate'] < 5:
        return "Consider changing your ad copy or targeting."
    else:
        return "Your campaign is performing well!"

# Example usage
if __name__ == "__main__":
    product_name = "Super Product"
    
    # Generate content for the product
    promo_content = generate_content(product_name)
    print(f"Generated Promo Content: {promo_content}")

    # Mock performance data
    performance_data = {
        'sales': [10, 20, 15],
        'clicks': [200, 300, 250]
    }
    
    # Analyze performance
    analysis_results = analyze_performance(performance_data)
    
    print(f"Total Sales: {analysis_results['total_sales']}")
    print(f"Conversion Rate: {analysis_results['conversion_rate']}%")
    
    # Optimize campaign based on analysis
    optimization_advice = optimize_campaign(analysis_results)
    
    print(f"Optimization Advice: {optimization_advice}")