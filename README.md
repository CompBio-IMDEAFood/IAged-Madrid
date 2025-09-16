# IAged-Madrid
A virtual research team addressing statistical challenges in the exploitation of EHR databases. This initiative builds on the [Virtual lab](https://www.nature.com/articles/s41586-025-09442-9) framework, which is structured around meetings designed to conduct virtual experiments, but here it takes a step further: aiming to produce a IA generated scientific article.

## An experiment within an experiment
The IAged-Madrid virtual research group is a team of large language model (LLM) agents to assist an experiment design.

## How it works
The scenario is composed by 7 consecutive discussions, since workflow design to the peer review process to obtain the final document.
* **Discussion 1:** Workflow design. In this first meeting of type **"individual_meeting"**, the user provide to the coordinator of the project, **the aim of the project** or the hypothesis to validate; a **dict database**, including the table names, and the column names of each table of the database. The last request is obtain the **deliverable**, a **provisional workflow**.
  
* **Discussion 2:** Refine the initial workflow. In this meeting of type **"group_meeting"**, also the provisional workflow is provided with the goal of refine it including all members team's insights. A conversational **scheme** is provided, explaining how much rounds of interventions and which team members will intervene throgout the meeting. These members will share their thoughts with the rest of members. The coordinator will convene the meeting, acting as moderator. The last request is obtain the **deliverable**, a **definitive workflow**.
  
* **Discussion 3:** Define a methodology. In this **"group_meeting"**, the experts that will develop the statisticals methods, will define how they will do. They will discusse about the procedure, the variable selection, the tools, the programming language, following a conversational **scheme**, this time with less interventors. he **coordinator** will convene the meeting, acting as moderator. At the end, the coordinator will synthesize the decissions in a summary, as **deliverable**.
  
* **Discussion 4:**
  * *Phase A:* In this phase, given a methodology/procedure to follow, *developers* will distribute the tasks and split the pipeline to follow in scripts. They will do in a conversation following the scheme provided. This time, the meeting will convened by one of the developers, acting as **moderator**. At the end the moderator will provide a python list of tuples, with each script_name\[0] assign to a responsible agent\[1].
  *  *Phase B:* In this phase, some team members will answer questions raised along phase A, contributing to solve doubts about some relevant decissions made in the code. The **deliverable** is a summary of solver questions.
