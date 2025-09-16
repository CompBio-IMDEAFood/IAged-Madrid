# IAged-Madrid
A virtual research team addressing statistical challenges in the exploitation of EHR databases. This initiative builds on the [Virtual lab](https://www.nature.com/articles/s41586-025-09442-9) framework, which is structured around meetings designed to conduct virtual experiments, but here it takes a step further: aiming to produce a IA generated scientific article.

## An experiment within an experiment
The IAged-Madrid virtual research group is a team of large language model (LLM) agents to assist an experiment design.

<img src="IAged_madrid_group.png" alt="Logo IAged-Madrid">

## An experiment within an experiment
The IAged-Madrid virtual research group is composed of large language model (LLM) agents assisting with experiment design.

## How it works
The process consists of 7 consecutive discussions, supported by a human user, spanning from workflow design to peer review to produce the final document.

* **Discussion 1: Workflow design.**  
  An **"individual_meeting"** where the user provides the project coordinator with the **aim of the project** or the hypothesis to be tested, as well as a **dictionary of database tables** with their corresponding column names. The deliverable is a **provisional workflow**.

* **Discussion 2: Refining the workflow.**  
  A **"group_meeting"** where the provisional workflow is reviewed and improved with input from all team members. A conversational **scheme** specifies the number of intervention rounds and the roles of participants. Members share their insights, and the coordinator moderates the session. The deliverable is a **definitive workflow**.

* **Discussion 3: Methodology definition.**  
  A **"group_meeting"** where statistical experts define the procedures, variable selection, tools, and programming languages to be used. A conversational **scheme** with fewer participants guides the discussion. The coordinator moderates and compiles the **deliverable**, a summary of decisions.

* **Discussion 4:**  
  * *Phase A:* Developers distribute tasks and divide the pipeline into scripts, following the agreed methodology. A developer moderates this session. The deliverable is a Python list of tuples pairing each `script_name` with its responsible agent.  
  * *Phase B:* Team members address questions raised during Phase A, clarifying coding decisions. The deliverable is a summary of resolved issues.

* **Discussion 5: Code development.**  
  A **working session** where the moderator initiates the coding phase. A conversation proceeds with `num_rounds = len(deliverable)` to implement all scripts defined in Discussion 4. The moderator summarizes key details for inclusion in the methodology section.  
  The resulting scripts are saved, and the human user executes them locally. Workflow results are stored in a string called `"results"`, which serves as input for the next discussion.

* **Discussion 6: Drafting the manuscript.**  
  * *Phase A:* A **group_meeting** where members share their perspectives and conclusions about the results, following a structured conversation.  
  * *Phase B:* Continuing from Phase A, the coordinator drafts the manuscript iteratively using a **dictionary of sections**, where keys are section names and values are drafting instructions.  
  The draft manuscript is saved, storing each `section_name` and its content in a string.

* **Discussion 7: Peer review simulation.**  
  The manuscript is embedded in the conference LaTeX template. Two review rounds are conducted, with comments from two reviewers. The coordinator then revises the manuscript based on feedback. The deliverable is the **final, conference-ready manuscript**.

## Requeriments
* requires-python = ">=3.10"
  * dependencies = [
    "virtual_lab",
    "pymysql",
    "notebook",
    "openai",
    "tiktoken",
    "tqdm"
]



