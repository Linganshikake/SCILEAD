# Efficient Scientific Progress Tracking: Leveraging Large Language Models for Automated Generation of Scientific Leaderboards

This software belongs to implementation for the manuscript named "Efficient Scientific Progress Tracking: Leveraging Large Language Models for Automated Generation of Scientific Leaderboards" The project pipeline consists of three main steps: extracting TDMR tuples from scientific papers, normalization and comparison with gold leaderboards. The output of one step becomes the input of another step. We also use our proposed ExSciLead as evaluation dataset.

## Requirements

```
conda create -n leaderboard_generation python=3.11
conda activate leaderboard_generation
pip install -r requirements.txt
```
We use [unstructured](https://docs.unstructured.io/open-source/introduction/quick-start) library to process PDF files. In order to utilize it in our experiments, along with its python installation ```pip install "unstructured[all-docs]"```, other system dependencies like [tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html) and [poppler](https://anaconda.org/conda-forge/poppler) must be installed as well.

From nltk library, ```punkt```, ```averaged_perceptron_tagger``` should be also installed.

## Preprocessing Papers

In this step, the papers from ExSciLead needs to be downloaded via links provided in the dataset. Then, you can preprocess PDF files to extract relevant chunks from main text as well as table information and save them. Therefore, you can repeatedly use the preprocessed documents for TDMR extraction process by different LLMs without additional computational overhead. You can simply run following command to preprocess PDF files and save relevant text chunks and tables. 

```
python doc_preprocess.py --process_id "an identifier for process" --papers_path /path/to/papers --prompt_file prompts.json --output_path /path/to/output
```

Parameter explanation:

* ```process_id```
  * A process id that is determined by you.

* ```papers_path```
  * Path to folder including PDF of papers.

* ```prompt_file```
  * Path to the prompt file. Default file is prompts.json

* ```output_path```
  * Path where processed documents are saved.

## TDMR Extraction

You can simply run following command to extract TDMR tuples from either PDFs files or pre-processed files. Output of this code will be ```output.json``` file including TDMR extraction along with source documents and ```config.json``` including experimental details. 

```
python tdm_extraction.py --env_file_path /path/to/env/file --exp_id "an identifier for exp" --processed_docs_path /path/to/processed_docs --papers_path /path/to/papers --prompt_file prompts.json --output_path /path/to/output --model_type "chosen model type" --model_version "version of the model" -- model_path /path/to/model --is_preprocessed_doc
```

Parameter explanation:

* ```env_file_path``` 
  * If you use GPT-4 Turbo, please specify the environment file path including AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT information. 

* ```exp_id```
  * An experiment id that is determined by you.

* ```processed_docs_path```
  * If you use preprocessed documents, please specify saved file path. Otherwise, use empty string.

* ```papers_path```
  * If you use PDF documents directly, please specify folder path including paper PDFs. Otherwise, use empty string.

* ```prompt_file```
  * Path to the prompt file. Default file is prompts.json

* ```output_path```
  * Path where extraction outputs are saved.

* ```model_type```
  * Type of the model that will be used in experiments. Please select one of the following options: {llama-2-chat-70b, Mixtral-8x7B-Instruct-v0.1, llama-3-instruct-70b, gpt4-turbo-128k}

* ```model_version```
  * Model version of GPT-4 Turbo. If you use other models, use empty string.

* ```model_path```
  * Model path for the selected open model. Please use local path or compatible huggingface name. If you use GPT-4 Turbo, use empty string. 

* ```is_preprocessed_doc```
  * Pass this flag if you use preprocessed documents. 

* ```max_new_tokens```
  * Maximum number of new generated tokens. Default value is 1024.

* ```seed```
  * Seed value for reproducibility. Default value is 0.

  
## Base Normalization

Base normalization assumes that the output section for each paper in ```output.json``` from ```tdm_extraction.py``` is a string that is in JSON readable format. Sometimes LLMs fail to follow this format. If so, please use format corrected version in the normalization process. Before starting you need to create ```normalization``` folder in the same ```output_path``` from TDMR extraction process.

```
python tdm_llm_normalization.py --gold_tdm_path /path/to/tdm_annotations.json  --tdm_output_path /same/output/path/tdmr/extraction/ --prompt_file prompts.json
```

Parameter explanation:

* ```gold_tdm_path``` 
  * Path to the gold TDMR dataset (tdm_annotations.json)

* ```tdm_output_path```
  * The same output path from TDMR extraction experiment. ```output.json``` and ```config.json``` should be there.

* ```prompt_file```
  * Path to the prompt file. Default file is prompts.json

* ```max_new_tokens```
  * Maximum number of new generated tokens. Default value is 1024.

* ```seed```
  * Seed value for reproducibility. Default value is 0.


## Partially Masking Normalization - Cold Start

Partially masking normalization and cold start make the same assumption as base normalization. Before starting you need to create ```masked_normalization``` or ```cold_start``` folder depending on normalization type in the same ```output_path``` from TDMR extraction process. For the first step of this normalization, you can simply run following command:

```
python tdm_llm_masked_normalization.py --gold_tdm_path /path/to/tdm_annotations.json --gold_leaderboard_path /path/to/leaderboards.json --tdm_output_path /same/output/path/tdmr/extraction/ --prompt_file prompts.json --cold_start
```

Parameter explanation:

Parameters are the same as base normalization except following.

* ```gold_leaderboard_path``` 
  * Path to the gold leaderboard dataset (leaderboards.json)

* ```cold_start```
  * Pass this flag if you want to use cold start normalization. Otherwise, partially masking normalization will be implemented.

For the second step including leaderboard-wise normalization, you can simply run

```
python leaderboard_llm_normalization.py --gold_leaderboard_path /path/to/leaderboards.json --tdm_output_path /same/output/path/tdmr/extraction/ --prompt_file prompts.json --cold_start
```

Parameter explanation: Parameters are the same as the first step except ```gold_tdm_path```.


## TDMR Evaluation

To evaluate model outputs in terms of exact tuple matching and individual item matching, you can simply run following command:

```
python tdm_eval.py --gold_data_path /path/to/tdm_annotations.json --normalized_tdm_output_path /path/to/normalized/tdmr/file/ --eval_results_path /path/for/average/results/ --eval_values_path /path/for/each/value/
```

Parameter explanation:

* ```gold_data_path``` 
  * Path to the gold TDMR dataset (tdm_annotations.json)

* ```normalized_tdm_output_path``` 
  * File that contains normalized generated tuples. File should be in JSON format and the key that contain tuple list should be 'normalized_output'.
  
* `eval_results_path`
  * JSON output path for average results for both exact tuple matching and individual item matching. 

* `eval_values_path`
  * JSON output path for individual scores for all papers


## Leaderboard Evaluation

For leaderboard-level evaluation of model outputs in terms of correctly captured paper - results values and rank biased overlap, you can simply run following command:

```
python leaderboard_eval.py --gold_leaderboards_path /path/to/leaderboards.json --masked_leaderboards_path /path/to/masked/leaderboard/file/ --normalized_tdm_output_path /path/to/normalized/tdmr/file/ --eval_results_path /path/for/average/results/ --eval_values_path /path/for/each/value/
```

Parameter explanation:

Parameters are the same as ```tdm_eval.py``` except following.

* ```gold_leaderboard_path``` 
  * Path to the gold leaderboard dataset (leaderboards.json)

* ```masked_leaderboards_path``` 
  * Path to the masked leaderboards file if the evaluated output is normalized via masking or cold start scheme. This file ("masked_leaderboards.json") can be found as an output of ```tdm_llm_masked_normalization.py```. If the base normalization applied, just use empty string.