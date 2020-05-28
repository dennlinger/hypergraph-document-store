# A Versatile Hypergraph Model for Document Collections

Andreas Spitz, Dennis Aumiller, Bálint Soproni and Michael Gertz<br/>
"A Versatile Hypergraph Model for Document Collections"<br/>
SSDBM 2020<br/>
DOI: https://doi.org/10.1145/1122445.1122456
preprint: TODO

This repository contains the main code, including all relevant results to reproduce the figures found in the submission. We additionally provide some more detailed analysis of our underlying dataset.


### Reproducing Figures from the Paper
Figures 4 and 5, including all relevant evaluation data, can be found in the folder `SSDBM_figures`; subfolders `document_vs_storage` and `window_size_vs_storage` are for Figure 4, and contain JSON files with the respective sizes.<br/>
To see which entities were evaluated specifically, see the `entities.json` in the `runtime_eval` subfolder.

### Data Definition
For Postgres, we list the various schemata in `Schema.md`, also see the definition in `docker/base11/createDBSchema.sql`, as well as `GenerateNewSchema.py` and `GenerateDyadicSQL.py`. <br/>
For Neo4j, see the `Neoj4` subfolder, which contains definitions for the respective models. Note that in Neo4j we need to create a temporary copy of the SQL tables due to the lack of composite primary keys in Neo4j.

### Query implementations
A detailed comparison between the PostgreSQL and Neo4j queries can be found in `Queries.md`.

### Dataset Analysis
To see a more descriptive analysis of the dataset used in the Evaluation section, see `old_eval/dataset_plots/`. In the `old_eval` folder, we also ship some more runtime analysis results on representative samples (entities "Donald Trump" (most frequently occurring entity), "Boris Johnson" (highly frequent), and "2016-07-09" (moderate occurrence frequency)) for various query tasks, performed only on our PostgreSQL implementation.

### Installation Instructions
For now, a complete reproduction of the results is out of scope, as the original dataset is hosted internally, and will generate a blob of over 800 GB in size for the complete evaluation data. For specific installation instructions and reasonable requests about the dataset, please reach out to Dennis Aumiller (`lastname (at) informatik.uni-heidelberg (dot) de`).

The implementation was performed under PostgreSQL 11.4, and Neo4j 3.5.11.

### Citation
If you are using our work, please cite our paper:

```
@inproceedings{Spitz2020Hypergraphs,
  author    = {Andreas Spitz and
               Dennis Aumiller and
               B\'alint Soproni and
               Michael Gertz},
  title     = {{A Versatile Hypergraph Model for Document Collections}},
  booktitle = {Proceedings of the 32nd International Conference on Scientific and
               Statistical Database Management, {SSDBM} 2020, Vienna, Austria,
               July 07-09, 2020},
  publisher = {{ACM}},
  year      = {2020},
  url       = {https://doi.org/10.1145/1122445.1122456},
  doi       = {10.1145/1122445.1122456},
}
```
