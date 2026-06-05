# Chargee P1 (Sparky & Flint)

Local Home Assistant integration for the Chargee P1 dongle. Reads your smart
meter data directly from Sparky or Flint over the Local API and feeds it into the
Home Assistant Energy dashboard - no cloud account required.

- Automatic mDNS discovery
- 100% local polling
- Energy dashboard ready (grid import/export and gas)
- Per-phase power, voltage and current
- Identify button and diagnostics

Requires Sparky firmware 95+ or Flint firmware 105+ with the Local API enabled
(Chargee app: Profile -> Address -> My House -> Local API).
