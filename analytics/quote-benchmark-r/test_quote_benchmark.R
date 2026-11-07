# Tests: Rscript test_quote_benchmark.R
source("quote_benchmark.R")
quote <- read.csv("quote.csv", stringsAsFactors = FALSE)
bench <- read.csv("benchmarks.csv", stringsAsFactors = FALSE)
terms <- read.csv("payment_terms.csv", stringsAsFactors = FALSE)

q <- benchmark_quote(quote, bench)
tot <- system_view(q)

# Benchmark arithmetic: 5 kWp x 55,000 = 275,000 low; 5 x 85,000 = 425,000 high
s <- q[q$component == "solar_installed", ]
stopifnot(s$bench_low == 275000, s$bench_high == 425000)
# Totals reconcile to the component sum
stopifnot(tot["quoted"] == sum(quote$quoted_inr))
stopifnot(tot["low"] == 275000 + 95000 + 200000, tot["high"] == 425000 + 160000 + 350000)
# Payment terms: 95% before delivery is high risk
p <- payment_risk(terms)
stopifnot(abs(p$pct_before_delivery - 0.95) < 1e-9, grepl("^HIGH", p$verdict))
# Counter sits between benchmark low and high
n <- negotiation(tot)
stopifnot(n["counter_inr"] >= tot["low"], n["counter_inr"] <= tot["high"])
# Missing benchmark is an error, not a silent NA
bad <- rbind(quote, data.frame(component = "drone_cleaning", spec = "x", qty = 1, unit = "unit", quoted_inr = 1))
stopifnot(inherits(try(benchmark_quote(bad, bench), silent = TRUE), "try-error"))
cat("all tests passed\n")
