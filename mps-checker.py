import torch
import time


class MPSChecker:
    def __init__(self):
        pass

    def check_mps(self):
        # Check that MPS is available
        if not torch.backends.mps.is_available():
            if not torch.backends.mps.is_built():
                print("MPS not available because the current PyTorch install was not "
                      "built with MPS enabled.")
            else:
                print("MPS not available because the current MacOS version is not 12.3+ "
                      "and/or you do not have an MPS-enabled device on this machine.")
        else:
            print("MPS is available.")


checker = MPSChecker()
checker.check_mps()

mps_device = torch.device("mps")
start_time = time.time()
model = torch.rand(30000, 24000)
model.to(mps_device)
print(model)
# End time
end_time = time.time()

# Compute and print the time taken
time_taken = end_time - start_time
print(f"Time taken: {time_taken} seconds")