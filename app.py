import bot o3
# import os
# import pandas as pd
# import re
# import streamlit as st
# import torch
# import spacy
# from transformers import BartTokenizer, BartForConditionalGeneration, AutoTokenizer, AutoModel
# from datetime import datetime
# from botocore.exceptions import NoCredentialsError, ClientError

# # Initialize S3 client
# s3_client = boto3.client('s3')
# s3_bucket = "amadeochat"

# # Function to download all files from a given S3 prefix (directory)
# def download_directory_from_s3(s3_bucket, s3_prefix, local_dir):
#     os.makedirs(local_dir, exist_ok=True)  # Create local directory if it doesn't exist

#     # List all files and "folders" (key prefixes) within the specified prefix (directory)
#     try:
#         response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)

#         if 'Contents' in response:
#             for obj in response['Contents']:
#                 s3_key = obj['Key']
#                 relative_path = s3_key[len(s3_prefix):]  # Get the relative path after the prefix
#                 local_file_path = os.path.join(local_dir, relative_path)

#                 if s3_key.endswith('/'):  # If the S3 key represents a folder
#                     os.makedirs(local_file_path, exist_ok=True)
#                     print(f"Created folder: {local_file_path}")
#                 else:  # If the S3 key represents a file
#                     os.makedirs(os.path.dirname(local_file_path), exist_ok=True)  # Ensure the directory exists
#                     s3_client.download_file(s3_bucket, s3_key, local_file_path)
#                     print(f"Downloaded file: {local_file_path}")
#         else:
#             print(f"No files found in {s3_prefix}")
#     except NoCredentialsError:
#         print("AWS credentials not found.")
#     except ClientError as e:
#         print(f"Error accessing S3: {e}")

# # Download models from their respective directories
# download_directory_from_s3(s3_bucket, "facebook-bart-large-cnn/", "/tmp/bart")
# download_directory_from_s3(s3_bucket, "finbert-tone/", "/tmp/finbert")
# download_directory_from_s3(s3_bucket, "en_core_web_sm/en_core_web_sm-3.7.1/", "/tmp/spacy/en_core_web_sm-3.7.1")

# # # Load spaCy model
# spacy_model_path = "/tmp/spacy/en_core_web_sm-3.7.1"  # Path to downloaded spaCy model
# nlp = spacy.load(spacy_model_path)

# # Load the BART model and tokenizer
# bart_model_path = "/tmp/bart"
# tokenizer=BartTokenizer.from_pretrained(bart_model_path)
# bart_model=BartForConditionalGeneration.from_pretrained(bart_model_path)

# # Load the FinBERT model and tokenizer
# finbert_model_path = "/tmp/finbert"
# finbert_tokenizer=AutoTokenizer.from_pretrained(finbert_model_path)
# finbert_model=AutoModel.from_pretrained(finbert_model_path)

# # print("Models loaded successfully.")


# # Streamlit app title
# st.title("Financial Data Query Assistant")

# # File uploader for Excel files
# uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

# if uploaded_file is not None:
#     # Read the uploaded file into a DataFrame
#     df = pd.read_excel(uploaded_file)

#     # Helper function to clean and convert value strings to float
#     def clean_value(value):
#         if isinstance(value, str):
#             cleaned_value = re.sub(r'[^\d.]+', '', value)
#             return float(cleaned_value) if cleaned_value else 0.0
#         return float(value)

#     # Function to get value based on metric and year
#     def get_value(metric, year):
#         result = df[(df['metrics'].str.lower() == metric.lower()) & (df['year'] == year)]
#         if not result.empty:
#             value = result['value'].values[0]
#             return clean_value(value)
#         return None

#     # Function to find the year with the highest value for a metric
#     def get_highest_year(metric):
#         metric_df = df[df['metrics'].str.lower() == metric.lower()]
#         if not metric_df.empty:
#             metric_df['cleaned_value'] = metric_df['value'].apply(clean_value)
#             max_value_row = metric_df.loc[metric_df['cleaned_value'].idxmax()]
#             return max_value_row['year'], max_value_row['cleaned_value']
#         return None, None

#     # Function to calculate changes between consecutive years
#     def calculate_changes(metric):
#         metric_df = df[df['metrics'].str.lower() == metric.lower()]
#         if not metric_df.empty:
#             metric_df = metric_df.sort_values(by='year')
#             metric_df['cleaned_value'] = metric_df['value'].apply(clean_value)
#             metric_df['change'] = metric_df['cleaned_value'].diff()
#             max_change_row = metric_df.loc[metric_df['change'].idxmax()]
#             min_change_row = metric_df.loc[metric_df['change'].idxmin()]
#             return (max_change_row['year'], max_change_row['change']), (min_change_row['year'], min_change_row['change'])
#         return None, None

#     # Function to generate a BART model response
#     def generate_response(query):
#         inputs = tokenizer.encode("summarize: " + query, return_tensors="pt", max_length=512, truncation=True)
#         summary_ids = bart_model.generate(inputs, max_length=150, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
#         return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

#     # Function to convert relative time expressions to specific years
#     def parse_relative_time(query):
#         current_year = datetime.now().year
#         if "last year" in query.lower():
#             return current_year - 1
#         elif "this year" in query.lower():
#             return current_year
#         elif "next year" in query.lower():
#             return current_year + 1
#         elif "recently" in query.lower():
#             return current_year
#         return None

#     # Function to find the closest matching metrics using FinBERT embeddings
#     def find_closest_metrics_finbert(query_metric, metrics_list, top_n=5):
#         # Tokenize and embed the query and metrics
#         query_tokens = finbert_tokenizer(query_metric.lower(), return_tensors='pt')
#         query_embedding = finbert_model(**query_tokens).last_hidden_state.mean(dim=1)
        
#         similarities = []
#         for metric in metrics_list:
#             metric_tokens = finbert_tokenizer(metric, return_tensors='pt')
#             metric_embedding = finbert_model(**metric_tokens).last_hidden_state.mean(dim=1)
#             similarity = torch.cosine_similarity(query_embedding, metric_embedding).item()
#             similarities.append((metric, similarity))
        
#         # Sort by similarity and return top_n similar metrics
#         similarities.sort(key=lambda x: x[1], reverse=True)
#         return [metric for metric, _ in similarities[:top_n]]

#     # Function to extract and match metrics from the query
#     def extract_and_match_metric(query, metrics_list):
#         doc = nlp(query)
#         for token in doc:
#             if token.text.lower() in metrics_list:
#                 return token.text.lower()
#         return None

#     # Main function to handle queries
#     def handle_query(query):
#         metrics_list = df['metrics'].str.lower().unique()
#         metric = extract_and_match_metric(query, metrics_list)
#         year = None
#         compare_year = None
#         aggregate_function = None
#         find_max = False
#         find_change = False
#         find_when_change = False
        
#         # Check for change-related keywords
#         if any(keyword in query.lower() for keyword in ["increase", "decrease", "difference", "change"]):
#             find_change = True
#             if any(keyword in query.lower() for keyword in ["most", "highest"]):
#                 find_when_change = "max"
#             elif any(keyword in query.lower() for keyword in ["least", "lowest"]):
#                 find_when_change = "min"
        
#         # Check for aggregate keywords
#         if "total" in query.lower() or "sum" in query.lower():
#             aggregate_function = "sum"
#         elif "average" in query.lower() or "mean" in query.lower():
#             aggregate_function = "mean"
#         elif "highest" in query.lower() or "maximum" in query.lower():
#             find_max = True
        
#         # If the exact metric is not found, find similar metrics
#         if not metric:
#             similar_metrics = find_closest_metrics_finbert(query, metrics_list, top_n=3)
#             if similar_metrics:
#                 similar_metrics_str = ', '.join(similar_metrics)
#                 response = (f"I couldn't find the exact metric '{query}', but here are some similar metrics you can ask about: "
#                             f"{similar_metrics_str}.")
#                 return response
#             else:
#                 return generate_response(query)
        
#         metric_found_message = ""
        
#         # Handle queries asking for the highest value
#         if metric and find_max:
#             year, value = get_highest_year(metric)
#             if year and value is not None:
#                 response = f"{metric_found_message} The highest {metric.upper()} was {value:.2f} in {year}."
#                 return response
#             else:
#                 return f"Sorry, I couldn't find any data for {metric.upper()}."
        
#         # Handle change-related queries
#         if find_change:
#             max_change, min_change = calculate_changes(metric)
#             if find_when_change == "max" and max_change:
#                 year, change = max_change
#                 response = f"The highest change in {metric.upper()} was {change:.2f} in {year}."
#                 return response
#             elif find_when_change == "min" and min_change:
#                 year, change = min_change
#                 response = f"The lowest change in {metric.upper()} was {change:.2f} in {year}."
#                 return response
#             elif max_change and min_change:
#                 max_year, max_change_val = max_change
#                 min_year, min_change_val = min_change
#                 response = (f"The highest change in {metric.upper()} was {max_change_val:.2f} in {max_year}. "
#                             f"The lowest change was {min_change_val:.2f} in {min_year}.")
#                 return response
#             else:
#                 return f"Sorry, I couldn't find any change data for {metric.upper()}."
        
#         # If an aggregate function is specified
#         if aggregate_function:
#             if aggregate_function == "sum":
#                 total_value = df[df['metrics'].str.lower() == metric].value.sum()
#                 return f"The total value for {metric.upper()} is {total_value:.2f}."
#             elif aggregate_function == "mean":
#                 average_value = df[df['metrics'].str.lower() == metric].value.mean()
#                 return f"The average value for {metric.upper()} is {average_value:.2f}."
        
#         # General query handling
#         value = get_value(metric, year)
#         if value is not None:
#             return f"The value for {metric.upper()} in {year} is {value:.2f}."
        
#         return generate_response(query)

#     # Input field for the query
#     user_query = st.text_input("Ask a question about financial data:")
    
#     if user_query:
#         response = handle_query(user_query)
#         st.write(response)
