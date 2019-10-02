---
title: {{name | title}}
authors:
- {{username}}
tags:
- knowledge
date: {{ now() | strftime('%Y-%m-%dT%H:%M:%S') }}

location: {{ location }}
format: {{ format }}
deprecated: false
md5_hash: {{ md5_hash }}

sources:
- database: Redshift
- dataset: another_dataset

schema:
{{schema}}
---
A short description of the dataset.

<!--more-->

# Content
Describe the content of this dataset.

# Procedure
Describe how this dataset was generated.

