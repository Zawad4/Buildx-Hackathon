from fastapi import APIRouter
from app.crypto.pqc_kem import MLKEM768Service

router = APIRouter(prefix="/crypto", tags=["Post-Quantum Cryptography"])

@router.post("/pqc-handshake")
def run_pqc_handshake():
    """
    Executes an experimental NIST FIPS 203 ML-KEM-768 quantum-safe key exchange.
    Returns latency, key lengths, and verification state for the live demonstration.
    """
    result = MLKEM768Service.run_demonstration_handshake()
    return result

