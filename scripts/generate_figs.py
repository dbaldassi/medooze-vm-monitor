#!/usr/bin/env python3

import yaml
import argparse
import os
import shutil

import plot
import plot_cgroup
import line_step

location_dict = {
    "BEST": 0,
    "UPPER_RIGHT": 1,
    "UPPER_LEFT": 2,
    "LOWER_LEFT": 3,
    "LOWER_RIGHT": 4,
    "RIGHT": 5,
    "CENTER_LEFT": 6,
    "CENTER_RIGHT": 7,
    "LOWER_CENTER": 8,
    "UPPER_CENTER": 9,
    "CENTER": 10,
    "OUT_TOP": 11
}

protocol_dict = {
    "plot": plot.process_and_plot,
    "stepbox": line_step.run,
    "plot_cgroup": plot_cgroup.process_and_plot
}

def no_protocol_defined(_):
    print("No protocol defined or unsupported protocol")

def parse_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def update_settings(settings, new_settings):
    for key,value in new_settings.items():
        if "-dir" in key:
            root = settings.get(key, None)
            settings[key] = "{}/{}".format(settings[key], new_settings[key]) if root else new_settings[key]
        elif key == "loc":
            settings[key] = location_dict[value]
        else:
            settings[key] = value # override already existing value if any

def parse_stage(name, stage, settings):
    print(f"[INFO] Generating figures for stage {name}: {stage.get('description', '')}")
    update_settings(settings, stage.get("settings", {}))

    # print(stage["figures"][0])
    for fig in stage.get("figures", {}):
        local_settings = dict(settings)
        update_settings(local_settings, fig)
        cwd = os.getcwd()

        os.chdir(local_settings["exp-dir"])

        protocol = local_settings.get("protocol", None)
        protocol_dict.get(protocol, no_protocol_defined)(local_settings)

        dest=local_settings["out-dir"]
        if not os.path.exists(dest):
            os.makedirs(dest)

        for f in os.listdir():
            if f.endswith(".pdf") and os.path.isfile(f):
                try:
                    shutil.move(f, os.path.join(dest, f))
                except:
                    print("ERROR")
                    pass

        os.chdir(cwd)

def parse_exp(name, exp, settings, stage_name=None):
    print(f"[INFO] Generating figures for experiment {name}: {exp.get('description', '')}")

    update_settings(settings, exp.get("settings", {}))

    stages = exp.get("stages", {})
    if stage_name:
        if stage_name in stages:
            parse_stage(stage_name, stages[stage_name], dict(settings))
    else:
        for stage_name, stage in stages.items():
            parse_stage(stage_name, stage, dict(settings))

def main():
    parser = argparse.ArgumentParser(description="Generate figures to visualize the tesbed results from a yaml config file")
    parser.add_argument("--config", type=str, default="config.yml", help="YAML config file path")
    parser.add_argument("--exp", type=str, help="Generate all figures of specified experiment")
    parser.add_argument("--stage", type=str, help="Generate all figures of specified stage within experiment")
    args = parser.parse_args()

    config = parse_yaml(args.config)

    settings = config.get("global-settings", {})
    print(args)
    if args.exp:
        if args.exp in config.get("exps", {}):
            exp = config["exps"][args.exp]
            parse_exp(args.exp, exp, settings, args.stage)
        else:
            print(f"[ERREUR] Experiment '{args.exp}' does not exist.")
    elif args.stage:
        print(f"[ERREUR] You must first specify an experiment to select a stage.")
    else:
        experiments = config.get("exps", {})

        for exp_name,exp in experiments.items():
            parse_exp(exp_name, exp, dict(settings))


if __name__ == "__main__":
    main()
