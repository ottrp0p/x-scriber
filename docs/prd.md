## Overview ## 

This is the design for x-scriber, a python based service that uses OpenAI whisper, OpenAI chat completions, and a local Django back end/front end server to support the following functionalities: 

1. Live microphone recording of a person talking about a technical or product requirement document
2. The chunking of the live stream into smaller audio files. 
3. Sending said chunked audio files to OpenAI whisper for transcription 
4. Consolidating two documents -- the raw the transcription as well as the self governed ontology of a technical requirement document that is incrementally improved by each chunk 


## Desired Folder structure ##


x-scriber/
│
├── manage.py
├── pyproject.toml / requirements.txt
├── .env                      
├── README.md
│
├── config/                   # project-wide settings & urls
│   ├── __init__.py
│   ├── settings.py           # single settings file is enough
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── xscriber/                 # the ONLY Django app
│   ├── __init__.py
│   ├── apps.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py              # optional
│   ├── modules/              # python module code, so we can easily strip out core logic if we one day swap front/back end deployment
│   │   ├── __init__.py
│   │   └── transcriber.py
│   ├── templates/xscriber/   # HTML templates
│   │   └── index.html
│   ├── static/xscriber/      # CSS, JS, etc.
│   └── tests/
│       ├── __init__.py
│       └── test_basic.py
│
├── data/                     # local input/output storage (user-facing), functions as local I/O
│   ├── project_metadata/     # creates a mapping between a project_name / desc and an assigned project_id 
│   ├── audio-recordings/     # creates a naming for audio recording chunks used, append {project_id}_audiochunk_{i}only to this folder. naming is , where i increments for each project id 
|   ├── raw-transcriptions/   # corresponds to openai whisper transcriptions to the audio chunks, {project_id}_transcription_{i}. similarly append only, never delete.        
│   └── output/               # {project_id}_trd.md, documents managed by a system that uses openai chat completion to manage and split and update document to iteratively edit



## CLAUDE.md rules ## 
Generate us a claude.md for this repo with the following rules. 
1. the agent is never allowed to edit anything under the django data folder. But this is after the initial agent setup. So do this last after all other tasks are completed-- we will allow the initial setup to write the template quickstart project id before locking the folder. 


## Components ## 

1. OpenAI whisper module/class -- python module to support connection to OpenAI whisper. 
    a. init methods
    b. transcribe method to hit their endpoint to receive a transcrption 
    c. save the transcription out to a set location (invocation of function in django to specify the naming and location of the data)
2. OpenAI chat completion -- python module to create a TRD structure document md and iteratively improve it based on transcription chunks. 
    a. library of ontology type prompts. help write set of prompts to describe common parts in an TRD/PRD that we might look for. 
    b. processing of the original transcription into changes we need to pass to all of the TRD/PRD subparts in the ontology 
    c. parsing the existing md document into the ontology to be changed 
    d. chat completion call to edit the ontology parts 
    e. writing the changed ontology back into a single md document 
3. Recording Handler - Django backend 
    a. This is to handle the live stream of microphone audio information 
    b. should create an active listener and open tunnel to the front end microphone access 
    c. as information comes in once we get to the set threshold (set t = # of seconds), saves out audio transcription to set location. Returns the locaiton if true (this location to be passed to whisper for processing)
4. Project Handler - Django backend 
    a. this handler should orchestrate between the recording handler, the openAI whisper module, and the openAI chat completion. sets the parameters for the submodules. 
    b. handles naming passes to all the submodules -- can be given an existing project ID or called to instantiate a new project where it will self select a new Id to name the project 
    b. should letting the recording handler with open channel to the front end to be async producing new audio files as they come in 
    c. as audio files get successfuly saved out, should queue jobs to openAI whisper to transcribe. what do to about retries and failures
    d. make seaprate queue for ontology enrichment. To be done in order, unless a retry and a failure happens on the transcription side which induces a skip. waits on its corresponding transcription job to finish
5. Frontend
    a. create a simple front end, involving four main panels. 
    b. the first is a project selector -- looking in the data folders depending on what project_id exist in output. we bring those in as selectable items to navigate 
    c. the second in a project viwer -- the project data are just TRD/PRD.md files. We want to load this in some scrollable readeable panel. This is to load only after the project is selector. Should default to the first project_id
    d. the 3rd is a transcription selector, after selecting a project, we show all of the transcription chunks that have been processed for this project id 
    e. the 4th is the transcription viewer, selecting which transcription file, displays the transcription text. 
    f. We need a button to initiate a new project_id. should create an empty project file as produe new project metadata in the data folder 
    g. Finally with a project selected, we need a record button that will connect to system microphone and kick off our process to begin the recording -> transcribe -> enrich cycle. 
    h. Need some kind of async/hook process from the backend where the front end says what we're currently processing. Needs timeouts 
    g. we should always start with some trivial test trd as project_id = 0 that should come as the standard. the gitingore should ignore all data except for the fake project_id 0 sample that we automatically render in the front end as a quick start reference. 



## TODO Tracking ## 

Create a md at the top level called TODO.md. You will write this in teh following fashion. 

For a plan created at time t, write down the timestamp, then the full todo list. Each on its own line. For this live session as you complete task, edit the tasks on each line to indicate whether they were finished or not. 

If a new invocation of writing the repo based off the trd/prd document. refer to the TODO.md and check what was completed during the last session before making a new plan. 


## Execution of tasks ## 
1. always check for the todo.md to know where we are. if not exist, make it exist, refer to the todo tracking section
2. git init this repo
3. Identify all tasks the user has to provide for you that cannot be contextually gathered by your own io. I expect this mainly has to do with permission setting and env variables. writing this into a user_todo.md. If a blocker for later steps, just list future todos and wait for user to confirm completion of his tasks. 
4. Prework to writing the components 
    - figure out what the interface contracts are between the components by running example inputs. Especially to external APIs (chat completion, whisper)
    - after figuring out interface contracts, plan a series of unit /regression tests for our components
    - write this out to interface.md on the top level if this doesn't exist 
5. writing the components 
    - focus on one function at a time in a component. follow a cycle of 
    - plan out all functions needed for component/class
    - write function logic 
    - develop test for function
    - test, use test output to iterate if need be 
    - once satisfied, git add changes to the function, add git commit -m "{description of the function added}"
    - do this for each function for each component. do this for all components. 


