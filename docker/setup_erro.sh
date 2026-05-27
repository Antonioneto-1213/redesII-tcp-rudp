
INTERFACE="eth0"

tc qdisc del dev $INTERFACE root 2>/dev/null

case "$1" in
  A)
    echo "Cenário A: 0% perda, 10ms delay"
    tc qdisc add dev $INTERFACE root netem delay 10ms
    ;;
  B)
    echo "Cenário B: 5% perda, 50ms delay"
    tc qdisc add dev $INTERFACE root netem delay 50ms loss 5%
    ;;
  C)
    echo "Cenário C: 10% perda, 100ms delay"
    tc qdisc add dev $INTERFACE root netem delay 100ms loss 10%
    ;;
  *)
    echo "Use: $0 [A|B|C]"
    ;;
esac

echo "Configuração atual:"
tc qdisc show dev $INTERFACE