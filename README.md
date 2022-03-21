# WCNES project

example code to transmit data from a cient to the basestation. 

The packet is structured as follows:
```
sequence number (1 Byte) | timestamp (4 Bytes) | random sequence (N Bytes)
```
The random sequence is seeded with the sequence number to generate unique and reproducible sequences for each packet. The check for bit errors in the statistics code expects this sequence. 
