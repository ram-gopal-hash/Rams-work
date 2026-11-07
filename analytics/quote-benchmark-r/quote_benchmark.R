#!/usr/bin/env Rscript
# Solar quotation benchmark: sign, negotiate (with a number) or walk away.
#
# A vendor quote is compared component by component against a researched
# market range, not against a single "rupees per watt" headline. The script:
#   1. builds the benchmark range per component and for the whole system,
#   2. places each quoted line within its range (0% = market low, 100% = high),
#   3. scores the payment terms (cash paid before delivery is credit risk),
#   4. proposes a counter-offer and a walk-away price,
#   5. prints a payback sensitivity grid (price x annual saving).
#
# Base R only, so it runs anywhere:  Rscript quote_benchmark.R
# Optional args: quote.csv benchmarks.csv payment_terms.csv annual_saving_inr
#
# All data in this folder is synthetic.

benchmark_quote <- function(quote, bench) {
  q <- merge(quote, bench, by = c("component", "unit"), all.x = TRUE)
  if (any(is.na(q$low_inr_per_unit))) {
    stop("no benchmark for: ", paste(q$component[is.na(q$low_inr_per_unit)], collapse = ", "))
  }
  q$bench_low  <- q$qty * q$low_inr_per_unit
  q$bench_high <- q$qty * q$high_inr_per_unit
  q$bench_mid  <- (q$bench_low + q$bench_high) / 2
  q$position_pct <- round(100 * (q$quoted_inr - q$bench_low) / (q$bench_high - q$bench_low))
  q$flag <- ifelse(q$quoted_inr > q$bench_high, "ABOVE RANGE",
            ifelse(q$quoted_inr < q$bench_low, "BELOW RANGE - check spec", "in range"))
  q[order(-q$quoted_inr), ]
}

system_view <- function(q) {
  tot <- c(quoted = sum(q$quoted_inr), low = sum(q$bench_low),
           mid = sum(q$bench_mid), high = sum(q$bench_high))
  tot["premium_over_high_pct"] <- round(100 * (tot["quoted"] / tot["high"] - 1), 1)
  tot
}

payment_risk <- function(terms) {
  before <- sum(terms$pct[terms$before_delivery])
  list(pct_before_delivery = before,
       verdict = if (before > 0.70) "HIGH: most cash leaves before goods arrive"
                 else if (before > 0.40) "MEDIUM" else "LOW")
}

# Counter at the benchmark midpoint; walk away above the benchmark high.
negotiation <- function(tot) {
  c(counter_inr = unname(round(tot["mid"], -3)),
    walk_away_above_inr = unname(round(tot["high"], -3)))
}

payback_grid <- function(prices, savings) {
  g <- outer(prices, savings, function(p, s) round(p / s, 1))
  dimnames(g) <- list(paste0("price ", format(prices, big.mark = ",")),
                      paste0("saving ", format(savings, big.mark = ",")))
  g
}

main <- function(args) {
  f <- function(i, default) if (length(args) >= i) args[[i]] else default
  quote <- read.csv(f(1, "quote.csv"), stringsAsFactors = FALSE)
  bench <- read.csv(f(2, "benchmarks.csv"), stringsAsFactors = FALSE)
  terms <- read.csv(f(3, "payment_terms.csv"), stringsAsFactors = FALSE)
  saving <- as.numeric(f(4, "70000"))

  q <- benchmark_quote(quote, bench)
  tot <- system_view(q)
  pay <- payment_risk(terms)
  neg <- negotiation(tot)

  cat("COMPONENT BENCHMARK (INR)\n")
  print(q[, c("component", "qty", "unit", "quoted_inr", "bench_low", "bench_high",
              "position_pct", "flag", "source_tag")], row.names = FALSE)
  cat(sprintf("\nSYSTEM  quoted %s | market %s to %s | premium over top of range %.1f%%\n",
              format(tot["quoted"], big.mark = ","), format(tot["low"], big.mark = ","),
              format(tot["high"], big.mark = ","), tot["premium_over_high_pct"]))
  cat(sprintf("PAYMENT %.0f%% before delivery -> %s\n", 100 * pay$pct_before_delivery, pay$verdict))

  decision <- if (tot["quoted"] > tot["high"] * 1.15) "WALK AWAY unless re-quoted"
              else if (tot["quoted"] > tot["high"] || pay$pct_before_delivery > 0.70) "NEGOTIATE"
              else "SIGN, subject to spec check"
  cat(sprintf("DECISION %s | counter at %s | walk away above %s\n", decision,
              format(neg["counter_inr"], big.mark = ","),
              format(neg["walk_away_above_inr"], big.mark = ",")))

  cat("\nPAYBACK SENSITIVITY (years, before subsidy)\n")
  prices <- round(c(tot["low"], tot["mid"], tot["high"], tot["quoted"]), -3)
  print(payback_grid(unname(prices), saving * c(0.8, 1, 1.2)))

  write.csv(q, "benchmark_output.csv", row.names = FALSE)
  invisible(list(q = q, tot = tot, pay = pay, neg = neg, decision = decision))
}

if (sys.nframe() == 0) main(commandArgs(trailingOnly = TRUE))
