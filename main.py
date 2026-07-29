#!/bin/python3

import argparse, pathlib, sys

import lib.compare as _compare
import lib.cache as _cache

if __name__ == "__main__":
    current_path = pathlib.Path(__file__).parent
    parser = argparse.ArgumentParser(prog = 'cpt', description = 'Competitve Programming Tools')
    subparsers = parser.add_subparsers(dest = 'command', help = 'Available subcommands')

    parser_compare = subparsers.add_parser('compare', help = 'Compare two programs by checking the output on the same input data.')
    parser_compare.add_argument("datagen", type = str, help = "Path of data generator executable")
    parser_compare.add_argument("program_a", type = str, help = "Path of program A")
    parser_compare.add_argument("program_b", type = str, help = "Path of program B")
    parser_compare.add_argument("-s", "--strategy", type = str, choices = ["limited_steps", "nonstop"], default = "nonstop", help = "Comparing strategy")
    parser_compare.add_argument("-m", "--mismatch", type = str, choices = ["continue", "stop", "pause"], default = "stop", help = "Action when two outputs differ")
    parser_compare.add_argument("-l", "--logging", type = str, choices = ["none", "mismatches", "all"], default = "mismatches", help = "When to preserve data files (Use `cpt recover` to recover)")
    parser_compare.add_argument("-n", "--num-steps", type = int, default = 10, help = "(Only when strategy=limited_steps) Number of steps")
    parser_compare.add_argument("-j", "--judger", type = str, default = str(current_path / "judgers" / "default.py"), help = "Path of judger executable.")
    parser_compare.add_argument("-t", "--max-runtime", type = str, default = "1.0", help = "Maximum runtime in seconds. Set to negative for no time limit. If set to tuple, the four numbers indicate time limit for (data generator, program A, program B, judger).")

    parser_cachelist = subparsers.add_parser('cache-list', help = 'List all saved cache files.')
    parser_cachelist.add_argument("-n", "--num", type = int, default = int(1e9), help = "Maximum numbers of cache directories to show")

    parser_cachepurge = subparsers.add_parser('cache-purge', help = 'Clear all cache files.')

    parser_recover = subparsers.add_parser('recover', help = 'Recover cache files to a target directory.')
    parser_recover.add_argument("cache_id", nargs = "?", type = str, default = None, help = "Cache ID to recover (default: most recent)")
    parser_recover.add_argument("-o", "--output", type = str, default = ".", help = "Target directory to recover into (default: current directory)")

    args = parser.parse_args()

    if args.command == "compare":
        _compare.work(args)
    elif args.command == "cache-list":
        _cache.list_files(args)
    elif args.command == "cache-purge":
        _cache.purge()
    elif args.command == "recover":
        _cache.recover(args)