#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

#初始化
#     init_session = """The following data will be sent to you in JSON format, containing the following fields:\n
# Question: The question I am posing to you\n
# Request: String, representing the HTTP request, using the placeholder request_str\n
# Response: String, representing the HTTP response, using the placeholder response_str\n"
# Answer: Please enter the answer to the question here\n"""

ANALYSIS_PROMPT = """Please analyze the following HTTP request and response for potential security vulnerabilities, focusing on the OWASP Top Ten vulnerabilities, such as SQL injection, XSS, CSRF, and other common web application security threats,\n
Format your answer as a list of items, with each point listing a vulnerability name and a brief description, as follows:\n
-- Vulnerability Name: Brief description of the vulnerability, excluding irrelevant information\n"""

SYSTEM_PROMPT = "Let's first understand the problem, extract relevant variables and their corresponding numerals, " \
             "and make and devise a complete plan. Then, let's carry out the plan, calculate intermediate variables " \
             "(pay attention to correct numerical calculation and commonsense), " \
             "solve the problem step by step, and show the answer."

# def get_prompt(type, prompt_name):
#     Few_Shot_Demo_Folder = ""
#     if type == 'zero_shot':
#         try:
#             samples = None
#             return samples, eval('prompt_{}'.format(prompt_name))
#         except NameError as e:
#             raise NameError('can\'t find prompt_id: {}'.format(prompt_name))
#     elif type == 'few_shot':
#         demo_file = Few_Shot_Demo_Folder + f'prompt_{prompt_name}.json'
#         try:
#             f = open(demo_file, 'r', encoding='utf-8')
#             demos_list = json.load(f)
#             demos_list = demos_list['demo']
#             demos = '\n'.join(demos_list)
#             return demos, eval('prompt_{}'.format(prompt_name))
#         except NameError as e:
#             raise NameError('can\'t find prompt_id: {}'.format(prompt_name))
#         except FileNotFoundError as e:
#             raise FileNotFoundError('can\'t find the demo file: {}'.format(demo_file))
#     else:
#         raise ValueError('not support learning_type: {}'.format(type))
#
# def construct_input(prompt, text):
#     inputs = 'Q:' + text + "\nA: " + prompt
#     return inputs