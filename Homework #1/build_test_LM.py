#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt
import math
import sys

# Constants
GRAM = 4
THRESHOLD = 0.7
K = 1


def build_LM(in_file):
    """
    Structure of the training file (in_file):
    <language> <text>
    ...
    """
    print("building language models...")

    with open(in_file, "r+") as file:
        lines = file.readlines()
        lines = [line.strip("\n") for line in lines]
        lines = [line.split(" ", 1) for line in lines]
        languages = [line[0] for line in lines]
        text = [line[1] for line in lines]

        LANGUAGE_PROFILES = {}

        language_set = set(languages)

        for lan in language_set:
            LANGUAGE_PROFILES[lan] = {}

        for lan, t in zip(languages, text):
            t = "_" * (GRAM - 1) + t + "_" * (GRAM - 1)
            grams = [t[i : i + GRAM] for i in range(len(t) - GRAM)]
            for gram in grams:
                if gram in LANGUAGE_PROFILES[lan]:
                    LANGUAGE_PROFILES[lan][gram] += 1
                else:
                    LANGUAGE_PROFILES[lan][gram] = 1

                for l in language_set:
                    if l != lan and gram not in LANGUAGE_PROFILES[l]:
                        LANGUAGE_PROFILES[l][gram] = 0

        # Add K smoothing
        for lan in LANGUAGE_PROFILES:
            for gram in LANGUAGE_PROFILES[lan]:
                LANGUAGE_PROFILES[lan][gram] += K

            count = sum(list(LANGUAGE_PROFILES[lan].values()))

            for gram in LANGUAGE_PROFILES[lan]:
                LANGUAGE_PROFILES[lan][gram] /= count

    return LANGUAGE_PROFILES


def test_LM(in_file, out_file, LM):
    """
    Structure for testing file (in_file):
    <text>

    Structure for output file (out_file):
    <language-label> <text>
    """
    print("testing language models...")

    output = []
    text = []

    with open(in_file, "r+") as file:
        lines = file.readlines()
        text = [line.strip("\n") for line in lines]

        for t in text:
            t = "_" * (GRAM - 1) + t + "_" * (GRAM - 1)
            grams = [t[i : i + GRAM] for i in range(len(t) - GRAM)]

            # LM is the language profiles created by build_LM
            not_in = min(
                [
                    sum([1 for gram in grams if gram not in LM[lan]]) / len(grams)
                    for lan in LM
                ]
            )
            if not_in >= THRESHOLD:
                output.append("other")
                continue

            pair = max(
                [
                    (
                        lan,
                        sum(
                            [
                                math.log(LM[lan][gram])
                                for gram in grams
                                if gram in LM[lan]
                            ]
                        ),
                    )
                    for lan in LM
                ],
                key=lambda x: x[1],
            )
            output.append(pair[0])

    with open(out_file, "w+") as file:
        _ = [file.write(o + " " + t + "\r\n") for o, t in zip(output, text)]

    return


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"
    )


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "b:t:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == "-b":
        input_file_b = a
    elif o == "-t":
        input_file_t = a
    elif o == "-o":
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
