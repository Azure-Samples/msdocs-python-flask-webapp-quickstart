import os
import base64
import zipfile

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, Response, jsonify)

app = Flask(__name__)

staging = "aGFtbXVyYWJpIHsKICAgIGRhdGFGcmFtZUluZm8gewogICAgICAgIGN1dG9mZkRhdGU9JHtZRUFSfSItIiR7TU9OVEh9Ii0iJHtEQVl9CiAgICAgICAgZnJlcXVlbmN5UnVsZUV4ZWN1dGlvbj0iPEZSRUNVRU5DSUE+IgogICAgICAgIHBoeXNpY2FsVGFyZ2V0TmFtZT0iPFRBQkxBX1JBVz4iCiAgICAgICAgdGFyZ2V0UGF0aE5hbWU9IjxSVVRBX1NUQUdJTkc+IgogICAgICAgIHV1YWE9IjxVVUFBX1JBVz4iCiAgICB9CiAgICBpbnB1dCB7CiAgICAgICAgb3B0aW9ucyB7CiAgICAgICAgICAgIDxERUxJTUlUQURPUj4KICAgICAgICAgICAgPE9QVElPTl9JTlBVVD4KICAgICAgICB9CiAgICAgICAgcGF0aHM9WwogICAgICAgICAgICAiPFJVVEFfU1RBR0lORz4iCiAgICAgICAgXQogICAgICAgIHNjaGVtYSB7CiAgICAgICAgICAgIHBhdGg9JHtBUlRJRkFDVE9SWV9VTklRVUVfQ0FDSEV9Ii9hcnRpZmFjdG9yeS8iJHtTQ0hFTUFTX1JFUE9TSVRPUll9Ii9zY2hlbWFzL2NvLzxVVUFBX01BU1RFUj4vcmF3LzxUQUJMQV9SQVc+L2xhdGVzdC88VEFCTEFfUkFXPi5vdXRwdXQuc2NoZW1hIgogICAgICAgIH0KICAgICAgICB0eXBlPSI8VElQT19BUkNISVZPPiIKICAgIH0KICAgIHJ1bGVzPVsKICAgICAgICB7CiAgICAgICAgICAgIGNsYXNzPSJjb20uZGF0aW8uaGFtbXVyYWJpLnJ1bGVzLmNvbXBsZXRlbmVzcy5Db21wbGV0ZW5lc3NSdWxlIgogICAgICAgICAgICBjb25maWcgewogICAgICAgICAgICAgICAgaWQgPSAiQ09fTVZQXzxUQUJMQV9SQVc+XzIuMV8wMDEiCiAgICAgICAgICAgICAgICBhY2NlcHRhbmNlTWluPTEwMC4wCiAgICAgICAgICAgICAgICBpc0NyaXRpY2FsPXRydWUKICAgICAgICAgICAgICAgIG1pblRocmVzaG9sZD0xMDAuMAogICAgICAgICAgICAgICAgdGFyZ2V0VGhyZXNob2xkPTEwMC4wCiAgICAgICAgICAgICAgICB3aXRoUmVmdXNhbHM9ZmFsc2UKICAgICAgICAgICB9CiAgICAgICAgfSwKCQk8Rk9STUFUT1M+CgkJPE5VTE9TPgogICAgICAgIHsKICAgICAgICAgICAgY2xhc3MgPSAiY29tLmRhdGlvLmhhbW11cmFiaS5ydWxlcy5jb25zaXN0ZW5jZS5EdXBsaWNhdGVSdWxlIgogICAgICAgICAgICBjb25maWcgPSB7CiAgICAgICAgICAgICAgICBhY2NlcHRhbmNlTWluPTEwMC4wCiAgICAgICAgICAgICAgICBpZCA9ICJDT19NVlBfPFRBQkxBX1JBVz5fNC4yXzAwMSIKICAgICAgICAgICAgICAgIGNvbHVtbnM9WwogICAgICAgICAgICAgICAgICAgIDxLRVlTPgogICAgICAgICAgICAgICAgXQogICAgICAgICAgICAgICAgaXNDcml0aWNhbD10cnVlCiAgICAgICAgICAgICAgICBtaW5UaHJlc2hvbGQ9MTAwLjAKICAgICAgICAgICAgICAgIHRhcmdldFRocmVzaG9sZD0xMDAuMAogICAgICAgICAgICAgICAgd2l0aFJlZnVzYWxzPXRydWUKICAgICAgICAgICAgfQogICAgICAgIH0KICAgIF0KfQ=="
raw = "aGFtbXVyYWJpIHsKICAgIGRhdGFGcmFtZUluZm8gewogICAgICAgIGN1dG9mZkRhdGU9JHtZRUFSfSItIiR7TU9OVEh9Ii0iJHtEQVl9CiAgICAgICAgZnJlcXVlbmN5UnVsZUV4ZWN1dGlvbj0iPEZSRUNVRU5DSUE+IgogICAgICAgIHBoeXNpY2FsVGFyZ2V0TmFtZT0iPFRBQkxBX1JBVz4iCiAgICAgICAgdGFyZ2V0UGF0aE5hbWU9IjxSVVRBX1NUQUdJTkc+IgogICAgICAgIHV1YWE9IjxVVUFBX1JBVz4iCiAgICB9CiAgICBpbnB1dCB7CiAgICAgICAgb3B0aW9ucyB7CiAgICAgICAgICAgIDxERUxJTUlUQURPUj4KICAgICAgICAgICAgPE9QVElPTl9JTlBVVD4KICAgICAgICB9CiAgICAgICAgcGF0aHM9WwogICAgICAgICAgICAiPFJVVEFfU1RBR0lORz4iCiAgICAgICAgXQogICAgICAgIHNjaGVtYSB7CiAgICAgICAgICAgIHBhdGg9JHtBUlRJRkFDVE9SWV9VTklRVUVfQ0FDSEV9Ii9hcnRpZmFjdG9yeS8iJHtTQ0hFTUFTX1JFUE9TSVRPUll9Ii9zY2hlbWFzL2NvLzxVVUFBX01BU1RFUj4vcmF3LzxUQUJMQV9SQVc+L2xhdGVzdC88VEFCTEFfUkFXPi5vdXRwdXQuc2NoZW1hIgogICAgICAgIH0KICAgICAgICB0eXBlPSI8VElQT19BUkNISVZPPiIKICAgIH0KICAgIHJ1bGVzPVsKICAgICAgICB7CiAgICAgICAgICAgIGNsYXNzPSJjb20uZGF0aW8uaGFtbXVyYWJpLnJ1bGVzLmNvbXBsZXRlbmVzcy5Db21wbGV0ZW5lc3NSdWxlIgogICAgICAgICAgICBjb25maWcgewogICAgICAgICAgICAgICAgaWQgPSAiQ09fTVZQXzxUQUJMQV9SQVc+XzIuMV8wMDEiCiAgICAgICAgICAgICAgICBhY2NlcHRhbmNlTWluPTEwMC4wCiAgICAgICAgICAgICAgICBpc0NyaXRpY2FsPXRydWUKICAgICAgICAgICAgICAgIG1pblRocmVzaG9sZD0xMDAuMAogICAgICAgICAgICAgICAgdGFyZ2V0VGhyZXNob2xkPTEwMC4wCiAgICAgICAgICAgICAgICB3aXRoUmVmdXNhbHM9ZmFsc2UKICAgICAgICAgICB9CiAgICAgICAgfSwKCQk8Rk9STUFUT1M+CgkJPE5VTE9TPgogICAgICAgIHsKICAgICAgICAgICAgY2xhc3MgPSAiY29tLmRhdGlvLmhhbW11cmFiaS5ydWxlcy5jb25zaXN0ZW5jZS5EdXBsaWNhdGVSdWxlIgogICAgICAgICAgICBjb25maWcgPSB7CiAgICAgICAgICAgICAgICBhY2NlcHRhbmNlTWluPTEwMC4wCiAgICAgICAgICAgICAgICBpZCA9ICJDT19NVlBfPFRBQkxBX1JBVz5fNC4yXzAwMSJoYW1tdXJhYmkgewogICAgZGF0YUZyYW1lSW5mbyB7CiAgICAgICAgY3V0b2ZmRGF0ZT0ke1lFQVJ9Ii0iJHtNT05USH0iLSIke0RBWX0KICAgICAgICBmcmVxdWVuY3lSdWxlRXhlY3V0aW9uPSI8RlJFQ1VFTkNJQT4iCiAgICAgICAgcGh5c2ljYWxUYXJnZXROYW1lPSI8VEFCTEFfUkFXPiIKICAgICAgICBzdWJzZXQ9IjxTVUJTRVQ+IgogICAgICAgIHRhcmdldFBhdGhOYW1lPSI8UlVUQV9SQVc+IgogICAgICAgIHV1YWE9IjxVVUFBX1JBVz4iCiAgICB9CiAgICBpbnB1dCB7CiAgICAgICAgcGF0aHM9WwoJCQkiPFJVVEFfUkFXPiIKCQldCiAgICAgICAgc2NoZW1hIHsKICAgICAgICAgICAgcGF0aD0ke0FSVElGQUNUT1JZX1VOSVFVRV9DQUNIRX0iL2FydGlmYWN0b3J5LyIke1NDSEVNQVNfUkVQT1NJVE9SWX0iL3NjaGVtYXMvY28vPFVVQUFfTUFTVEVSPi9yYXcvPFRBQkxBX1JBVz4vbGF0ZXN0LzxUQUJMQV9SQVc+Lm91dHB1dC5zY2hlbWEiCiAgICAgICAgfQogICAgICAgIHR5cGU9YXZybwogICAgICAgIG9wdGlvbnN7CiAgICAgICAgICAgIGNhc3RNb2RlPW5vdFBlcm1pc3NpdmUKICAgICAgICAgICAgZGlzYWJsZUF1dG9tYXRpY0NvbnZlcnNpb25zPXRydWUKICAgICAgICB9CiAgICB9CiAgICBydWxlcz1bCiAgICAgICAgewogICAgICAgICAgICBjbGFzcz0iY29tLmRhdGlvLmhhbW11cmFiaS5ydWxlcy5jb21wbGV0ZW5lc3MuQmFzaWNQZXJpbWV0ZXJDb21wbGV0ZW5lc3NSdWxlIgogICAgICAgICAgICBjb25maWcgewogICAgICAgICAgICAgICAgaWQgPSAiQ09fTVZQXzxUQUJMQV9SQVc+XzIuMl8wMDEiCiAgICAgICAgICAgICAgICBhY2NlcHRhbmNlTWluPTEwMC4wCiAgICAgICAgICAgICAgICBkYXRhVmFsdWVzIHsKICAgICAgICAgICAgICAgICAgICBvcHRpb25zIHsKICAgICAgICAgICAgICAgICAgICAgICAgPERFTElNSVRBRE9SPgogICAgICAgICAgICAgICAgICAgICAgICA8T1BUSU9OX0lOUFVUPgogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgICBwYXRocz1bCiAgICAgICAgICAgICAgICAgICAgICAgICI8UlVUQV9TVEFHSU5HPiIKICAgICAgICAgICAgICAgICAgICBdCiAgICAgICAgICAgICAgICAgICAgc2NoZW1hIHsKICAgICAgICAgICAgICAgICAgICAgICAgcGF0aD0ke0FSVElGQUNUT1JZX1VOSVFVRV9DQUNIRX0iL2FydGlmYWN0b3J5LyIke1NDSEVNQVNfUkVQT1NJVE9SWX0iL3NjaGVtYXMvY28vPFVVQUFfTUFTVEVSPi9yYXcvPFRBQkxBX1JBVz4vbGF0ZXN0LzxUQUJMQV9SQVc+Lm91dHB1dC5zY2hlbWEiCiAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgICAgIHR5cGU9IjxUSVBPX0FSQ0hJVk8+IgogICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgaXNDcml0aWNhbD10cnVlCiAgICAgICAgICAgICAgICBtaW5UaHJlc2hvbGQ9MTAwLjAKICAgICAgICAgICAgICAgIHRhcmdldFRocmVzaG9sZD0xMDAuMAogICAgICAgICAgICAgICAgd2l0aFJlZnVzYWxzPWZhbHNlCiAgICAgICAgICAgIH0KICAgICAgICB9CiAgICBdCn0KCiAgICAgICAgICAgICAgICBjb2x1bW5zPVsKICAgICAgICAgICAgICAgICAgICA8S0VZUz4KICAgICAgICAgICAgICAgIF0KICAgICAgICAgICAgICAgIGlzQ3JpdGljYWw9dHJ1ZQogICAgICAgICAgICAgICAgbWluVGhyZXNob2xkPTEwMC4wCiAgICAgICAgICAgICAgICB0YXJnZXRUaHJlc2hvbGQ9MTAwLjAKICAgICAgICAgICAgICAgIHdpdGhSZWZ1c2Fscz10cnVlCiAgICAgICAgICAgIH0KICAgICAgICB9CiAgICBdCn0="
master= "aGFtbXVyYWJpIHsKICAgIGRhdGFGcmFtZUluZm8gewogICAgICAgIGN1dG9mZkRhdGU9JHtZRUFSfSItIiR7TU9OVEh9Ii0iJHtEQVl9CiAgICAgICAgZnJlcXVlbmN5UnVsZUV4ZWN1dGlvbj0iPEZSRUNVRU5DSUE+IgogICAgICAgIHBoeXNpY2FsVGFyZ2V0TmFtZT0iPFRBQkxBX01BU1RFUj4iCiAgICAgICAgc3Vic2V0PSI8U1VCU0VUPiIKICAgICAgICB0YXJnZXRQYXRoTmFtZT0iPFJVVEFfTUFTVEVSPiIKICAgICAgICB1dWFhPSI8VVVBQV9NQVNURVI+IgogICAgfQogICAgaW5wdXQgewogICAgICAgIHBhdGhzPVsKCQkJIjxSVVRBX01BU1RFUj4iCgkJXQogICAgICAgIHNjaGVtYSB7CiAgICAgICAgICAgIHBhdGg9JHtBUlRJRkFDVE9SWV9VTklRVUVfQ0FDSEV9Ii9hcnRpZmFjdG9yeS8iJHtTQ0hFTUFTX1JFUE9TSVRPUll9Ii9zY2hlbWFzL2NvLzxVVUFBX01BU1RFUj4vbWFzdGVyLzxUQUJMQV9NQVNURVI+L2xhdGVzdC88VEFCTEFfTUFTVEVSPi5vdXRwdXQuc2NoZW1hIgogICAgICAgIH0KICAgICAgICB0eXBlPXBhcnF1ZXQKICAgICAgICBvcHRpb25zewogICAgICAgICAgICBvdmVycmlkZVNjaGVtYT10cnVlCiAgICAgICAgICAgIGluY2x1ZGVNZXRhZGF0YUFuZERlbGV0ZWQ9dHJ1ZQogICAgICAgIH0KICAgIH0KICAgIHJ1bGVzPVsKICAgICAgICB7CiAgICAgICAgICAgIGNsYXNzPSJjb20uZGF0aW8uaGFtbXVyYWJpLnJ1bGVzLmNvbXBsZXRlbmVzcy5CYXNpY1BlcmltZXRlckNvbXBsZXRlbmVzc1J1bGUiCiAgICAgICAgICAgIGNvbmZpZyB7CiAgICAgICAgICAgICAgICBpZCA9ICJDT19NVlBfPFRBQkxBX01BU1RFUj5fMi4zXzAwMSIKICAgICAgICAgICAgICAgIGFjY2VwdGFuY2VNaW49MTAwLjAKICAgICAgICAgICAgICAgIGRhdGFWYWx1ZXMgewogICAgICAgICAgICAgICAgICAgIG9wdGlvbnMgewogICAgICAgICAgICAgICAgICAgICAgICBjYXN0TW9kZT1ub3RQZXJtaXNzaXZlCiAgICAgICAgICAgICAgICAgICAgICAgIGRpc2FibGVBdXRvbWF0aWNDb252ZXJzaW9ucz10cnVlCiAgICAgICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgICAgIHBhdGhzPVsKICAgICAgICAgICAgICAgICAgICAgICAgIjxSVVRBX1JBVz4iCiAgICAgICAgICAgICAgICAgICAgXQogICAgICAgICAgICAgICAgICAgIHNjaGVtYSB7CiAgICAgICAgICAgICAgICAgICAgICAgIHBhdGg9JHtBUlRJRkFDVE9SWV9VTklRVUVfQ0FDSEV9Ii9hcnRpZmFjdG9yeS8iJHtTQ0hFTUFTX1JFUE9TSVRPUll9Ii9zY2hlbWFzL2NvLzxVVUFBX01BU1RFUj4vcmF3LzxUQUJMQV9SQVc+L2xhdGVzdC88VEFCTEFfUkFXPi5vdXRwdXQuc2NoZW1hIgogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgICB0eXBlPSJhdnJvIgogICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgaXNDcml0aWNhbD10cnVlCiAgICAgICAgICAgICAgICBtaW5UaHJlc2hvbGQ9MTAwLjAKICAgICAgICAgICAgICAgIHRhcmdldFRocmVzaG9sZD0xMDAuMAogICAgICAgICAgICAgICAgd2l0aFJlZnVzYWxzPWZhbHNlCiAgICAgICAgICAgIH0KICAgICAgICB9CiAgICBdCn0K"
procesamiento = "aGFtbXVyYWJpIHsKICAgIGRhdGFGcmFtZUluZm8gewogICAgICAgIGN1dG9mZkRhdGU9JHtZRUFSfSItIiR7TU9OVEh9Ii0iJHtEQVl9CiAgICAgICAgZnJlcXVlbmN5UnVsZUV4ZWN1dGlvbj0iPEZSRUNVRU5DSUE+IgogICAgICAgIHBoeXNpY2FsVGFyZ2V0TmFtZT0iPFRBQkxBX01BU1RFUj4iCiAgICAgICAgc3Vic2V0PSI8U1VCU0VUPiIKICAgICAgICB0YXJnZXRQYXRoTmFtZT0iPFJVVEFfTUFTVEVSPiIKICAgICAgICB1dWFhPSI8VVVBQV9NQVNURVI+IgogICAgfQogICAgaW5wdXQgewogICAgICAgIHBhdGhzPVsKCQkJIjxSVVRBX01BU1RFUj4iCgkJXQogICAgICAgIHNjaGVtYSB7CiAgICAgICAgICAgIHBhdGg9JHtBUlRJRkFDVE9SWV9VTklRVUVfQ0FDSEV9Ii9hcnRpZmFjdG9yeS8iJHtTQ0hFTUFTX1JFUE9TSVRPUll9Ii9zY2hlbWFzL2NvLzxVVUFBX01BU1RFUj4vbWFzdGVyLzxUQUJMQV9NQVNURVI+L2xhdGVzdC88VEFCTEFfTUFTVEVSPi5vdXRwdXQuc2NoZW1hIgogICAgICAgIH0KICAgICAgICB0eXBlPXBhcnF1ZXQKICAgICAgICBvcHRpb25zewogICAgICAgICAgICBvdmVycmlkZVNjaGVtYT10cnVlCiAgICAgICAgICAgIGluY2x1ZGVNZXRhZGF0YUFuZERlbGV0ZWQ9dHJ1ZQogICAgICAgIH0KICAgIH0KICAgIHJ1bGVzPVsKICAgICAgICA8Rk9STUFUT1M+CiAgICAgICAgPE5VTE9TPgogICAgICAgIHsKICAgICAgICAgICAgY2xhc3MgPSAiY29tLmRhdGlvLmhhbW11cmFiaS5ydWxlcy5jb25zaXN0ZW5jZS5EdXBsaWNhdGVSdWxlIgogICAgICAgICAgICBjb25maWcgPSB7CiAgICAgICAgICAgICAgICBhY2NlcHRhbmNlTWluPTEwMC4wCiAgICAgICAgICAgICAgICBpZCA9ICJDT19NVlBfPFRBQkxBX1JBVz5fNC4yXzAwMSIKICAgICAgICAgICAgICAgIGNvbHVtbnM9WwogICAgICAgICAgICAgICAgICAgIDxLRVlTPgogICAgICAgICAgICAgICAgXQogICAgICAgICAgICAgICAgaXNDcml0aWNhbD10cnVlCiAgICAgICAgICAgICAgICBtaW5UaHJlc2hvbGQ9MTAwLjAKICAgICAgICAgICAgICAgIHRhcmdldFRocmVzaG9sZD0xMDAuMAogICAgICAgICAgICAgICAgd2l0aFJlZnVzYWxzPXRydWUKICAgICAgICAgICAgfQogICAgICAgIH0KICAgIF0KfQo="
job = "ewogICAgIl9pZCIgOiAiPEpPQj4iLAogICAgImRlc2NyaXB0aW9uIiA6ICJKb2IgPEpPQj4gY3JlYXRlZCB3aXRoIFNreW5ldCBmb3IgPFBST1lFQ1Q+LiIsCiAgICAia2luZCIgOiAicHJvY2Vzc2luZyIsCiAgICAicGFyYW1zIiA6IHsKICAgICAgICAiY29uZmlnVXJsIiA6ICIke3JlcG9zaXRvcnkuZW5kcG9pbnQudmRjfS8ke3JlcG9zaXRvcnkucmVwby5zY2hlbWFzfS9raXJieS9jby88Q09ORklHUlVURT4iCiAgICB9LAogICAgInJ1bnRpbWUiIDogImtpcmJ5My1sdHMiLAogICAgInNpemUiIDogIlMiLAogICAgInN0cmVhbWluZyIgOiBmYWxzZQp9Cg=="
conf = "ewogICJwcm95ZWN0IiA6ICJQcm95ZWN0byIsCiAgImZyZWN1ZW5jaWEiIDogIkRhaWx5IiwJCiAgImFsaWFzdGFibGEiOiAieGRhaWNjZXJpbmZjZXJ0aWZpY3BvbCIsCiAgInRpcG9fYXJjaGl2byIgOiAiY3N2IiwKICAidGlwb2hlYWRlciIgOiAic2luSGVhZGVyIC8gY29uSGVhZGVyIC8gZml4ZWQiLAogICJkZWxpbWl0YWRvciIgOiAiICd8JywgJy8nLCAnOyfigKYiLAogICJydXRhX3N0YWdpbmciOiAiL2luL3N0YWdpbmcvZGF0YXgvYmlwcy9DQklQU19EMDJfXCIkez9ZRUFSfSR7P01PTlRIfSR7P0RBWX1cIl94ZGFpY2Nlcl9pbmZfY2VydGlmaWNfcG9sLnR4dCIsCiAgInJ1dGFfcmF3IjogIi9kYXRhL3Jhdy9jaWN4L2RhdGEvdF9jaWN4X3hkYWljY2VyX2luZl9jZXJ0aWZpY19wb2wiLAogICJydXRhX21hc3RlciI6ICIvZGF0YS9tYXN0ZXIvYmlwcy9kYXRhL3RfYmlwc194ZGFpY2Nlcl9pbmZfY2VydGlmaWNfcG9sIiwKICAic3Vic2V0IiA6ICJwYXJ0aXRpb25fZGF0YV95ZWFyX2lkPSdcIiR7P1lFQVJ9XCInIEFORCBwYXJ0aXRpb25fZGF0YV9tb250aF9pZD0nXCIkez9NT05USH1cIicgQU5EIHBhcnRpdGlvbl9kYXRhX2RheV9pZD0nXCIkez9EQVl9XCInIiwKICAibWFuZGF0b3Jpb3MiIDogInBvbGljeV9pZCxpbnN1cmFuY2VfY2VydGlmaWNhdGVfaWQscG9saWN5X3N0YXJ0X2RhdGUscG9saWN5X2VuZF9kYXRlLGNvdmVyYWdlX21vZGlmaWNhdGlvbl9pZCIsCiAgImxsYXZlcyIgOiAicG9saWN5X2lkLGluc3VyYW5jZV9jZXJ0aWZpY2F0ZV9pZCxjb3ZlcmFnZV9tb2RpZmljYXRpb25faWQiCn0="


def optionvalues(variable: str) -> str:
    patrones = {
        "_number": "^[0-9]+$",
        "_date": "^[0-9\\s\\-\\.\\:]+$",
        "_id": "^[0-9A-Za-z]+$",
        "_amount": "^[0-9\\.]+$"
    }

    for sufijo, patron in patrones.items():
        if variable.endswith(sufijo):
            return patron

    return "^[0-9A-Za-z ,.-]+$"
def validacion(variable: str) -> str:
    if variable.endswith("_number"):
        return "^[0-9]+$"
    elif variable.endswith("_date"):
        return "^[0-9\\s\\-\\.\\:]+$"
    elif variable.endswith("_id"):
        return "^[0-9A-Za-z]+$"
    elif variable.endswith("_amount"):
        return "^[0-9\\.]+$"
    else:
        return "^[0-9A-Za-z ,.-]+$"    

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(directory=os.getcwd(), path=filename, as_attachment=True)

@app.route('/hello', methods=['POST'])
def hello():
   print('Request for hello page received with form data: %s' % request.form)
   try:
       aliastabla =request.form.get('aliastabla')
       name = request.form.get('name')
       for key, value in request.form.items():
           print(f'Field name: {key}, Field value: {value}')
       datosBase = ""
       tipoEje = request.form.get('fase')
       if tipoEje == 'staging':
           datosBase = staging
       elif tipoEje == 'raw':
           datosBase = raw
       elif tipoEje == 'master':
           datosBase = master
       elif tipoEje == 'procesamiento':
           datosBase = procesamiento
       proyecto =request.form.get('proyecto')
       ruta_staging =request.form.get('ruta_staging')
       ruta_raw =request.form.get('ruta_raw')
       ruta_master =request.form.get('ruta_master')
       tipo_archivo =request.form.get('tipo_archivo')
       frecuencia =request.form.get('frecuencia')
       subset =request.form.get('subset')
       mandatorios =request.form.get('mandatorios')
       llaves =request.form.get('llaves')
       delimitador =request.form.get('delimitador')
       tabla_raw = os.path.basename(ruta_raw)
       tabla_master = os.path.basename(ruta_master)
       uuaa_raw = tabla_raw.split("_")[1]
       uuaa_master = tabla_master.split("_")[1]
       textollaves = llaves.split(',')
       optionv = optionvalues(request.form.get('tipoheader'))
       textomandatorios = mandatorios.split(',')
       llavesrules = ""
       mandatoriosrules = ""
       regostrollaves = 0
       mandatorioint = 0
       keys = ""
       for campo in textollaves:
        keys = keys + '"'+campo+'",'
       for campo in textomandatorios:
        regostrollaves = regostrollaves +1
        llavesrules = llavesrules + '{\n            class = "com.datio.hammurabi.rules.validity.NotNullValidationRule"\n            config = {\n                id = "CO_MVP_'+tabla_raw+'_3.1_'+str(regostrollaves).rjust(3, '0')+'"\n                column = "'+campo+'"\n                acceptanceMin=100.0\n                isCritical=true\n                minThreshold=100.0\n                targetThreshold=100.0\n                withRefusals=true\n            }\n        },\n		'
        mandatorioint = mandatorioint +1
        mandatoriosrules = mandatoriosrules + '{\n            class = "com.datio.hammurabi.rules.validity.FormatValidationRule"\n            config = {\n                id = "CO_MVP_'+tabla_raw+'_3.2_'+str(mandatorioint).rjust(3, '0')+'"\n                column = "'+campo+'"\n                format = "'+validacion(campo)+'"\n                acceptanceMin=100.0\n                isCritical=true\n                minThreshold=100.0\n                targetThreshold=100.0\n                withRefusals=true\n            }\n        },\n		'
       decoded_bytes = base64.b64decode(datosBase)
       decoded_string = decoded_bytes.decode('utf-8')
       decoded_bytesJob = base64.b64decode(job)
       decoded_stringJob = decoded_bytesJob.decode('utf-8')

       reemplazos = {
        '<UUAA_MASTER>': uuaa_master,
        '<UUAA_RAW>': uuaa_raw,
        '<TABLA_RAW>': tabla_raw,
        '<FRECUENCIA>': frecuencia,
        '<RUTA_STAGING>' : ruta_staging,
        '<RUTA_RAW>' : ruta_raw,
        '<TIPO_ARCHIVO>' : tipo_archivo,
        '<DELIMITADOR>' : "delimiter=" + '"' + delimitador + '"',
        '<OPTION_INPUT>' : optionv,
        '<NULOS>': llavesrules,
        '<FORMATOS>':mandatoriosrules,
        '<KEYS>' : keys[:-1],
        '<SUBSET>' : subset,
        '<TABLA_MASTER>' : tabla_master,
        '<RUTA_MASTER>' : ruta_master
       }
       tablaes = ""
       jobname = ""
       rutaconf = ""
       fase = ""
       if(tipoEje == 'staging'):
        fase = "staging" #<-----
        tablaes = tabla_raw
        jobname = uuaa_master+"-co-hmm-qlt-"+aliastabla+"s-01"
        rutaconf = uuaa_master+"/staging/"+tabla_raw+"/${dq.conf.version}/"+tabla_raw+"-01.conf"
       elif(tipoEje == 'raw'):
        fase = "raw" #<-----
        tablaes = tabla_raw
        jobname = uuaa_master+"-co-hmm-qlt-"+aliastabla+"r-01"
        rutaconf = uuaa_master+"/rawdata/"+tabla_raw+"/${dq.conf.version}/"+tabla_raw+"-01.conf"
       elif(tipoEje == 'master' or tipoEje == 'procesamiento'):
        fase = "master" #<-----
        tablaes = tabla_master
        jobname = uuaa_master+"-co-hmm-qlt-"+aliastabla+"m-01"
        rutaconf = uuaa_master+"/masterdata/"+tabla_master+"/${dq.conf.version}/"+tabla_master+"-01.conf"
       reemplazosJob = {
        '<JOB>': jobname,
        '<PROYECT>' : proyecto,
        '<CONFIGRUTE>': rutaconf
       }
       print(f'tabla Remmplazos: {reemplazosJob}')

       for clave, valor in reemplazos.items():
        #print(f'tabla LLAVE: {clave}')
        #print(f'tabla VALOR: {valor}')
        decoded_string = decoded_string.replace(clave, valor)
       print(f'tabla Final: {decoded_string}')
       for clave, valor in reemplazosJob.items():
        decoded_stringJob = decoded_stringJob.replace(clave, valor)
       print(f'tabla Final2: {decoded_stringJob}') 


   #Se crea una variable que guarda la ruta del archivo .conf o .json dentro de una carpeta que lleva el nombre de la fase (staging, raw o master)
       ruta_archivo_conf = tablaes + '-01.conf'
       ruta_archivo_json = tablaes + '-01.json'
       #with open(ruta_archivo_conf, 'w', encoding='utf-8') as nuevo_archivo7:
       # nuevo_archivo7.write(decoded_string)
       #with open(ruta_archivo_json, 'w', encoding='utf-8') as nuevo_archivo5:
       # nuevo_archivo5.write(decoded_stringJob)
        # Crear un archivo zip con los archivos .conf y .json
       # zip_filename = tablaes + '-config.zip'
       # with zipfile.ZipFile(zip_filename, 'w') as zipf:
       #     zipf.write(ruta_archivo_conf)
       #     zipf.write(ruta_archivo_json)
       # print(f'Archivo zip creado: {zip_filename}')
       # os.remove(ruta_archivo_conf)
       # os.remove(ruta_archivo_json)
       zip_filename = tablaes + '-config.zip'
       with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.writestr(tablaes + '-01.conf', decoded_string)
        zipf.writestr(tablaes + '-01.json', decoded_stringJob)
       print(f'Archivo zip creado: {zip_filename}')

       #rint(f'tabla Raw: {tabla_raw}')
       #print(f'tabla Master: {tabla_master}')
       #print(f'Error EJE: {keys}')
       #print(f'Nombre Tabla : {mandatoriosrules}')
       print(f'<a href =" {ruta_archivo_json}" target="_black">archivo Json</a>')
       print(f'<a href =" {ruta_archivo_conf}" target="_black">archivo Conf </a>')
       print('Request for hello page received with name=%s' % name)
   
       conf_download_link = url_for('download_file', filename=ruta_archivo_conf)
       json_download_link = url_for('download_file', filename=ruta_archivo_json)
       zip_download_link = url_for('download_file', filename=zip_filename)
       return render_template('hello.html', zip_download_link=zip_download_link)

   except Exception as e:
       print(f'Error de Ejecución : {e}')
       ##return redirect(url_for('index'))
       return redirect(url_for('index'))
if __name__ == '__main__':
   app.run()
