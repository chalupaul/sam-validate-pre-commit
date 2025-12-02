from __future__ import annotations

import argparse
import multiprocessing
import subprocess


def run_sam(command: str) -> int:
    try:
        result = subprocess.run(  # noqa: S602
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        if result.stderr != "":
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(e.stderr)
        return e.returncode
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="sam-validate",
        description="A pre-commit hook to validate sam templates.",
    )
    parser.add_argument("-n", "--no-lint", action="store_true", default=False)
    parser.add_argument(
        "-r",
        "--region",
        type=str,
        required=False,
        help="set the AWS Region of the service.",
    )
    parser.add_argument(
        "-p",
        "--profile",
        type=str,
        required=False,
        help="choose a specific profile from your "
        + "credential file to get AWS credentials.",
    )
    parser.add_argument(
        "-e",
        "--config-env",
        type=str,
        default="default",
        help="environment name specifying default "
        + "parameter values in the configuration file.",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        type=str,
        default="samconfig.toml",
        help="configuration file containing default parameter values.",
    )
    parser.add_argument(
        "-b",
        "--beta-features",
        action="store_true",
        default=False,
        help="enable/Disable beta features.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="turn on debug logging to print debug messages generated"
        + " by AWS SAM CLI and display timestamps.",
    )
    parser.add_argument("filenames", nargs="*", type=str, default=[])
    args = parser.parse_args()

    cmds: list[str] = []
    cmd_parts: list[str] = ["sam validate"]

    if args.region is not None:
        cmd_parts.append(f"--region {args.region}")

    if args.profile is not None:
        cmd_parts.append(f"--profile {args.profile}")

    cmd_parts.append(f"--config-env {args.config_env}")

    cmd_parts.append(f"--config-file {args.config_file}")

    if args.debug:
        cmd_parts.append("--debug")

    if args.beta_features:
        cmd_parts.append("--beta-features")
    else:
        cmd_parts.append("--no-beta-features")

    if not args.no_lint:
        cmd_parts.append("--lint")

    cmd = " ".join(cmd_parts)
    if len(args.filenames) == 0:
        cmds.append(cmd)
    else:
        for arg in args.filenames:
            cmds.extend(f"{cmd} -t {arg}")

    num_args: int = len(cmds)
    with multiprocessing.Pool(processes=num_args) as pool:
        results = pool.map(run_sam, cmds)
        for _, res in enumerate(results):
            if res != 0:
                return res
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
