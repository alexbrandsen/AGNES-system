# coding=utf-8
# Copyright 2022 Alex Brandsen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Dutch archaeological NER data, Fold 4"""

import os

import datasets


logger = datasets.logging.get_logger(__name__)


_CITATION = """\
@inproceedings{brandsen-etal-2020-creating,
    title = "Creating a Dataset for Named Entity Recognition in the Archaeology Domain",
    author = "Brandsen, Alex  and
      Verberne, Suzan  and
      Wansleeben, Milco  and
      Lambers, Karsten",
    editor = "Calzolari, Nicoletta  and
      B{\'e}chet, Fr{\'e}d{\'e}ric  and
      Blache, Philippe  and
      Choukri, Khalid  and
      Cieri, Christopher  and
      Declerck, Thierry  and
      Goggi, Sara  and
      Isahara, Hitoshi  and
      Maegaard, Bente  and
      Mariani, Joseph  and
      Mazo, H{\'e}l{\`e}ne  and
      Moreno, Asuncion  and
      Odijk, Jan  and
      Piperidis, Stelios",
    booktitle = "Proceedings of the Twelfth Language Resources and Evaluation Conference",
    month = may,
    year = "2020",
    address = "Marseille, France",
    publisher = "European Language Resources Association",
    url = "https://aclanthology.org/2020.lrec-1.562",
    pages = "4573--4577",
    abstract = "In this paper, we present the development of a training dataset for Dutch Named Entity Recognition (NER) in the archaeology domain. This dataset was created as there is a dire need for semantic search within archaeology, in order to allow archaeologists to find structured information in collections of Dutch excavation reports, currently totalling around 60,000 (658 million words) and growing rapidly. To guide this search task, NER is needed. We created rigorous annotation guidelines in an iterative process, then instructed five archaeology students to annotate a number of documents. The resulting dataset contains {\textasciitilde}31k annotations between six entity types (artefact, time period, place, context, species {\&} material). The inter-annotator agreement is 0.95, and when we used this data for machine learning, we observed an increase in F1 score from 0.51 to 0.70 in comparison to a machine learning model trained on a dataset created in prior work. This indicates that the data is of high quality, and can confidently be used to train NER classifiers.",
    language = "English",
    ISBN = "979-10-95546-34-4",
}
"""

_DESCRIPTION = """\
Dutch archaeological NER data, Fold 4
"""

_URLS = {
    "train": "train.txt",
    "dev": "dev.txt",
    "test": "test.txt",
}



class dutch_archaeo_ner_fold4Config(datasets.BuilderConfig):
    """BuilderConfig for dutch_archaeo_ner_fold4"""

    def __init__(self, **kwargs):
        """BuilderConfig for dutch_archaeo_ner_fold4.
        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(dutch_archaeo_ner_fold4Config, self).__init__(**kwargs)


class dutch_archaeo_ner_fold4(datasets.GeneratorBasedBuilder):
    """dutch_archaeo_ner_fold4 dataset."""

    BUILDER_CONFIGS = [
        dutch_archaeo_ner_fold4Config(name="conll2003", version=datasets.Version("1.0.0"), description="dutch_archaeo_ner_fold4 dataset"),
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "tokens": datasets.Sequence(datasets.Value("string")),
                    "ner_tags": datasets.Sequence(
                        datasets.features.ClassLabel(
                            names=[
                                "O",
                                "B-ART",
                                "I-ART",
                                "B-CON",
                                "I-CON",
                                "B-LOC",
                                "I-LOC",
                                "B-MAT",
                                "I-MAT",
                                "B-PER",
                                "I-PER",
                                "B-SPE",
                                "I-SPE",
                            ]
                        )
                    ),
                }
            ),
            supervised_keys=None,
            homepage="https://aclanthology.org/2020.lrec-1.562/",
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        downloaded_files = dl_manager.download_and_extract(_URLS)

        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"filepath": downloaded_files["train"]}),
            datasets.SplitGenerator(name=datasets.Split.VALIDATION, gen_kwargs={"filepath": downloaded_files['dev']}),
            datasets.SplitGenerator(name=datasets.Split.TEST, gen_kwargs={"filepath": downloaded_files['test']}),
        ]

    def _generate_examples(self, filepath):
        logger.info("⏳ Generating examples from = %s", filepath)
        with open(filepath, encoding="utf-8") as f:
            guid = 0
            tokens = []
            ner_tags = []
            for line in f:
                if line.startswith("-DOCSTART-") or line == "" or line == "\n":
                    if tokens:
                        yield guid, {
                            "tokens": tokens,
                            "ner_tags": ner_tags,
                        }
                        guid += 1
                        tokens = []
                        ner_tags = []
                else:
                    # tokens are space separated
                    splits = line.split(" ")
                    tokens.append(splits[0])
                    ner_tags.append(splits[1].rstrip())
            # last example
            if tokens:
                yield guid, {
                    "tokens": tokens,
                    "ner_tags": ner_tags,
                }