from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy import NaN
from pylab import rcParams

rcParams["figure.figsize"] = 16, 4

def readfile(filename):
    types = {
        "seq": int,
        "time_tx": float,
        "time_rx": float,
        "payload": str,
        "rssi": int,
    }
    df = pd.read_csv(
        StringIO(" ".join(l for l in open(filename))),
        skiprows=0,
        header=None,
        dtype=types,
        delim_whitespace=False,
        delimiter="|",
    )
    df.columns = ["seq", "time_tx", "time_rx", "payload", "rssi"]
    df.dropna(inplace=True)
    # print(df.describe())
    return df

def parse_payload(payload_string):
    tmp = map(lambda x: int(x, base=16), payload_string.split())
    return list(tmp)


def compute_sequence(seed, length):
    A1 = 1664525
    C1 = 1013904223
    RAND_MAX1 = (1 << 31) - 1  #
    MAX_BYTE = (1 << 8) - 1  # one byte
    num = seed | (1 << 4)  # seed (4 bites) is part of the seq number
    seq = list()
    for _ in range(length):  # generate the random payload byte by byte
        num = (num * A1 + C1) & RAND_MAX1
        seq.append(num & MAX_BYTE)
    return seq


def popcount(n):
    return bin(n).count("1")


def compute_bit_errors(payload, sequence, PACKET_LEN=32):
    return sum(
        map(
            popcount,
            (
                np.array(payload[:PACKET_LEN])
                ^ np.array(sequence[: len(payload[:PACKET_LEN])])
            ),
        )
    )


# def compute_ber(df, PACKET_LEN):
#     packets = len(df)
    
#     # dataframe records the bit error for each packet
#     error = pd.DataFrame(columns=['seq', 'bit_errors'])
#     # seq number initialization
#     error.seq = range(df.seq[0], df.seq[packets-1]+1)
#     # bit_errors list initialization
#     error.bit_errors = [list() for x in range(len(error))]
    
#     file_size = len(error) * PACKET_LEN * 8
    
#     # start count the error bits
#     for idx in range(packets):
#         # return the matched row index for the specific seq number in log file
#         error_idx = error.index[error.seq == df.seq[idx]][0]
#         # compute the bit errors
#         payload = parse_payload(df.payload[idx])
#         sequence = compute_sequence(df.seq[idx], PACKET_LEN)
#         error.bit_errors[error_idx].append(compute_bit_errors(payload, sequence, PACKET_LEN=PACKET_LEN))

#     # total bit error counter initialization
#     counter = 0
#     # for the lost packet 
#     for l in error.bit_errors:
#         if l == []: 
#             counter += PACKET_LEN*8 # when the seq number is lost, consider the entire packet payload as error
#         else:
#             counter += min(l) # when the seq number received several times, consider the minimum error
#     print(error)
#     return counter / file_size

def replace_seq(df, MAX_SEQ):
    df['new_seq'] = None
    count = 0
    df.iloc[0, df.columns.get_loc('new_seq')] = df.seq[0]
    for idx in range(1,len(df)):
        if df.seq[idx] < df.seq[idx-1] - 50:
            count += 1
            # for the counter reset scanrio, replace the seq value with order
        df.iloc[idx, df.columns.get_loc('new_seq')] = MAX_SEQ*count + df.seq[idx]
    return df

def compute_ber(df, PACKET_LEN=32, MAX_SEQ=256):
    packets = len(df)
    
    # dataframe records the bit error for each packet
    error = pd.DataFrame(columns=['seq', 'bit_errors'])
    # seq number initialization
    print(df.seq[packets-1]+1)
    error.seq = range(df.seq[0], df.seq[packets-1]+1)
    # bit_errors list initialization
    error.bit_errors = [list() for x in range(len(error))]
    
    file_size = len(error) * PACKET_LEN * 8
    
    # start count the error bits
    for idx in range(packets):
        # return the matched row index for the specific seq number in log file
        error_idx = error.index[error.seq == df.seq[idx]][0]
        # compute the bit errors
        payload = parse_payload(df.payload[idx])
        seq = df.seq[idx] % MAX_SEQ
        sequence = compute_sequence(seq, PACKET_LEN)
        error.bit_errors[error_idx].append(compute_bit_errors(payload, sequence, PACKET_LEN=PACKET_LEN))

    # total bit error counter initialization
    counter = 0
    # for the lost packet 
    for l in error.bit_errors:
        if l == []: 
            counter += PACKET_LEN*8 # when the seq number is lost, consider the entire packet payload as error
        else:
            counter += min(l) # when the seq number received several times, consider the minimum error
    print(error)
    return counter / file_size, error

