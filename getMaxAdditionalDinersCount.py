# The function sums up the potential additional diners from all available gaps to arrive at the final maximum count.


from typing import List

def getMaxAdditionalDinersCount(N: int, K: int, M: int, S: List[int]) -> int:
    # Set defined constraints
  if M == N:
    return 0
  
  num_seats: int = 0
  k_plus: int = K + 1
  seated: List[int] = sorted(S)

  if seated[0] > k_plus:
    first: int = seated[0] - 1

    if first - k_plus == 1:
      num_seats += 1
    else:
      num_seats += (first // k_plus)

  if seated[-1] < (N - K - 1):
    num_seats += ((N - seated[-1]) // k_plus)

  for i in range(0, M):
    if i < M - 1:
      spaces: int = seated[i + 1] - seated[i]
      if spaces > k_plus:
        num_seats += (spaces // k_plus) - 1

  return num_seats
