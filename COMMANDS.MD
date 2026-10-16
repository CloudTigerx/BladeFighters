$env:BF_W_TOP_MATCH="0.0"; `
$env:BF_W_COLOR_ADJ="2.8"; `
$env:BF_W_CLUSTER="0.8"; $env:BF_CLUSTER_CAP="4.0"; `
$env:BF_W_ISOLATED="-2.2"; `
$env:BF_W_RAISE_GUARD="-1.2"; $env:BF_RAISE_BASE_DELTA="3.0"; `
$env:BF_W_CENTER="0.2"; `
$env:BF_EMERGENCY_SAFESET="1"; `
$env:BF_W_TOP_RISK="-10000"; `
$env:BF_COL_CAP="11"; $env:BF_W_COL_CAP="-2.0"
$env:BF_W_BASE_BOOST="0.6"; $env:BF_BASE_FOCUS_K="2"; $env:BF_BASE_EARLY_HEIGHT="6"
$env:BF_W_CONNECT="0.4"; $env:BF_CONNECT_CAP="4.0"
$env:BF_TOP_MATCH_MIN_GAIN="1.2"; $env:BF_TOP_MATCH_MAX_HOLES="0"
$env:BF_CLEAR_MODE_FRAC="0.5"            # enter clear mode at 50% height
$env:BF_CLEAR_MODE_BOOST="1.5"           # stronger safety in clear mode
$env:BF_COMBO_MODE_BOOST="1.15"          # slightly stronger grouping in combo mode
$env:BF_W_CENTER="0.15"
$env:BF_W_COLOR_ADJ="3.0"
$env:BF_W_CLUSTER="0.9"; $env:BF_CLUSTER_CAP="4.0"
$env:BF_W_ISOLATED="-2.5"
$env:BF_W_NEXT_HINT="0.30"
$env:BF_W_BASE_BOOST="0.8"; $env:BF_BASE_FOCUS_K="2"; $env:BF_BASE_EARLY_HEIGHT="7"
$env:BF_W_CONNECT="0.6"; $env:BF_CONNECT_CAP="4.0"
$env:BF_CLEAR_MODE_FRAC="0.45"
$env:BF_CLEAR_MODE_BOOST="1.6"
$env:BF_W_HOLES="-10.0"; $env:BF_W_BUMP="-0.7"; $env:BF_W_SEAL_WELL="-4.0"
$env:BF_W_RAISE_GUARD="-1.8"; $env:BF_RAISE_BASE_DELTA="3.0"
$env:BF_COL_CAP="10"; $env:BF_W_COL_CAP="-2.5"
$env:BF_EMERGENCY_SAFESET="1"; $env:BF_W_TOP_RISK="-10000"
$env:BF_HYSTERESIS_BONUS="0.5"
$env:BF_W_HORIZ_BRIDGE="0.9"     # strengthen horizontal preference
$env:BF_W_VERT_STACK="-1.2"      # punish vertical towers without gain
$env:BF_VERT_STACK_DELTA="2.0"   # how much above neighbors counts as a tower
$env:BF_VERT_STACK_GAIN_MIN="1.4" # require stronger local gain to allow vertical lift
python -m swordfighting_new.pygame_client --enemy-difficulty insane

$env:BF_AI_DIFFICULTY="mono"
$env:BF_AI_MONO_COLOR="red"
$env:BF_AI_BREAKER_PROB="1"

$env:BF_MONO_COLOR=green
python -m swordfighting_new.pygame_client