from jinja2 import Environment, FileSystemLoader
import yaml

ENV = Environment(loader=FileSystemLoader('./'))

with open("config.yaml") as _:
    dict =  yaml.load(_)

# Print dictionary generated from yaml    
print dict

# Render template and print generated config to console
template = ENV.get_template("template.text")
print template.render(config=dict)