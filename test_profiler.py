import time
from orchestrator.profiler import Profiler

p = Profiler()

p.start("Memory")
time.sleep(0.3)
p.stop("Memory")

p.start("Research")
time.sleep(0.6)
p.stop("Research")

p.start("LLM")
time.sleep(1.2)
p.stop("LLM")

p.report()