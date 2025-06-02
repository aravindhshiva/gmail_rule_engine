# Gmail Rule Engine

A powerful CLI tool for managing Gmail messages through customizable rules. This tool allows you to load emails from your Gmail account and perform automated actions based on predefined rules.

## Features

- Load and store Gmail messages locally
- Process emails based on customizable rules
- Support for various Gmail actions (marking as read/unread, adding/removing labels)
- Local SQLite database for email storage
- Rule-based automation for email maintenance

## Prerequisites

- Python 3.10 or higher
- OAuth 2.0 credentials

## Installation

> #### OAuth 2.0 Credentials
> To run the application, you will need a `credentials.json` file from the Google Cloud Console, which must be placed inside the `config` directory.


There are two ways to install the package:

### Option 1: Using the Setup Script (Recommended)

Simply `source` the setup script which will create a virtual environment and install the package:
```bash
source setup
```
Do NOT execute the setup file i.e. don't run `./setup`. The file has to be sourced to run it in the same shell.

### Option 2: Manual Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
# or
.venv\Scripts\activate  # On Windows
```

2. Install the package:

```bash
pip install -e .  # in editable mode
# or 
pip install .
```

This will install the CLI as `gmailre`.

## Configuration

1. Configure rules in the `rule_engine/rules.json` file.

## Usage

The CLI tool `gmailre` provides three main modes of operation:

### 1. Initialize Database

Initialize the SQLite database for storing email data:
```bash
gmailre --init  # skips if the database already exists
```

To force re-initialization (deletes existing database, and reinitializes it):
```bash
gmailre --init --force-init
```

### 2. Load Emails

Load emails from Gmail into the local database:
```bash
gmailre --load
```

### 3. Process Rules

Process the loaded emails according to the rules defined in `rules.json`:
```bash
gmailre --process
```

## Rule Configuration

Rules are defined in JSON format. Here's an example structure:
```json
{
    "conditionType": "ALL",
    "rules": [
        {
            "field": "subject",
            "predicate": "equals",
            "value": "Thank You For Your Purchase"
        }
    ],
    "actions": [
        {
            "type": "move_message",
            "destination": "INBOX"
        },
        {
            "type": "mark_as_unread"
        }
    ]
}
```

### Available Fields
- subject
- from_email
- to_email
- received_date
- body

### Available Predicates

- for `subject`,`from_email`,`to_email`,`body`:
    - equals
    - does_not_equal
    - contains
    - does_not_contain
- for `received_date`:
    - less_than_months
    - greater_than_months
    - less_than_days
    - greater_than_days

### Available Actions
- move_message (requires destination, currently supports "INBOX", "SPAM", "TRASH")
- mark_as_read
- mark_as_unread

## Further Developments

There are avenues for extending the features of this CLI. Some of the potential developments include:

1. Extending the support for multiple RuleSets i.e. more than one ruleset should be supported.
2. Allowing add, update and delete of rules from the CLI.
3. Support additional move destinations like "STARRED", "IMPORTANT" as well as custom labels.
4. Instead of loading the whole database every time with all emails, we could utilize partial synchronization measures.

## Author

aravindhshiva

## Version

1.0.1