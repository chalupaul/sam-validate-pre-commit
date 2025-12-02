# sam-validate-pre-commit

This pre-commit hook checks all templates you configure it to know about at the same time.

### Background
AWS SAM has this kind of annoying behavior where validating a template with `sam validate` will only work on one template at a time, even if you have nested stacks defined in other files.

For example, if you have a template.yaml file that has this content:

```
---
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: foobar
Resources:
  ImageBuilderFoo:
    Type: AWS::Serverless::Application
    Properties:
      Location: .aws-sam/templates/imagebuilder.yaml
      Parameters:
        KMSKeyArn: !GetAtt KMSKey.Arn
```

When you run `sam validate`, sam never expands the Location property, and just assumes you know what you're doing. You can put any contents you want into imagebuilder.yaml and `sam validate` wouldn't know the difference.

### Usage

The most simple example is this entry in your .pre-commit-config.yaml file:

```
  - repo: https://github.com/chalupaul/sam-validate-pre-commit
    rev: v1.0.0
    hooks:
      - id: sam-validate
```

By default, this will run against ./template.yaml, ./template.yml, and any yaml files in ./.aws-sam or its subdirectories. Feel free to change the files directive to anything you wish. For example, if you have template.yaml and foobar.yaml as your templates in the standard location, you can just set this in the pre-commit definition
```
files: ^(template|foobar).yaml
```

Personally, I put my templates all in .aws-sam/templates to keep them out of the way.

### Sam Arguments
Almost every argument that `sam validate` can take are expressed in this pre-commit, however every template will be run with the same arguments. If you happen to need different sets, you'll need to use two different top level pre-commit-hooks.yaml entries.

This example turns on debugging and beta features for one file, but the main template.yaml remains the same:

```
  - repo: https://github.com/chalupaul/sam-validate-pre-commit
    rev: v1.0.0
    hooks:
      - id: sam-validate
        files: template.yaml
        args: [-e dev]
      - id: sam-validate
        files: foobar.yaml
        args: [--debug, --beta-features, -m 4]
```

#### Notes on arguments
- `--lint` is on by default
- `--save-params` is not exposed to the pre-commit hook so you don't blow away your config.
- `--beta-features|--no-beta-features` is always included, based on what the value of -b|--beta-features is. If you pass the flag, you get the features. Don't pass the flag, don't get the features.
- `--max-concurrent|-m` sets the number of concurrent processes. By default, this number is set to the number of files you have, but you can override it here (say if it makes your cpu fan spin up).
