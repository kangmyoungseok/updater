from decimal import Decimal

def get_mint_mean_period(mint_data_transaction,initial_timestamp):
    count = len(mint_data_transaction)
    if(count == 0):
      return 0
    mint_time_add = 0
    for transaction in mint_data_transaction:
      mint_time_add = mint_time_add + int(transaction['timestamp']) - initial_timestamp
    return mint_time_add / count

def get_swap_mean_period(swap_data_transaction,initial_timestamp):
    count = len(swap_data_transaction)
    if(count == 0):
      return 0
    swap_time_add = 0
    for transaction in swap_data_transaction:
      swap_time_add = swap_time_add +  int(transaction['timestamp']) - initial_timestamp
    return swap_time_add / count

def get_burn_mean_period(burn_data_transaction,initial_timestamp):
    count = len(burn_data_transaction)
    if(count == 0):
      return 0
    burn_time_add = 0
    for transaction in burn_data_transaction:
      burn_time_add = burn_time_add + int(transaction['timestamp']) - initial_timestamp
    return burn_time_add / count

def swap_IO_rate(swap_data_transaction,index):
  swapIn = 0
  swapOut = 0
  if(index == 1): #amount0이 이더.
    for data in swap_data_transaction:
      if(data['amount0In'] == '0'): #amount0Out이 0이 아니란 말. 
        swapOut = swapOut + 1
      else:   
        swapIn = swapIn + 1
  else:         #amount1이 이더
    for data in swap_data_transaction:
      if(data['amount1In'] == '0'):
        swapOut = swapOut + 1
      else:
        swapIn = swapIn +1
  
  return swapIn,swapOut 

def get_last_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction):
  #mint_data_transaction은 0일 수가 없다. 
  swap_len = len(swap_data_transaction)
  burn_len = len(burn_data_transaction)
  #Case 1 Swap / Burn 전부 0 인경우
  if(swap_len == 0 and burn_len == 0):
    return int(mint_data_transaction[-1]['timestamp'])
  #Case 2 Swap_transaction이 0 인경우
  if(swap_len == 0):
    return int(max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp']))
  #Case 3 Burn Transaction이 0 인경우
  if(burn_len == 0):
    return int(max(mint_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']))
  #Case 4 전부다 있는 경우
  return int(max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']))
  
def get_swap_amount(swap_data_transaction,j,eth_amountIn,eth_amountOut):
  if(swap_data_transaction[j][eth_amountIn] == '0'): #amountIn이 0 이면 out이라는 거지.
    return Decimal(swap_data_transaction[j][eth_amountOut]) * (-1)
  else:
    return Decimal(swap_data_transaction[j][eth_amountIn])

def get_timestamp(data_transaction,index):
  try:
    return data_transaction[index]['timestamp']
  except:
    return '99999999999'

def check_rugpull(before_transaction_Eth, current_Eth):
  if ( Decimal(current_Eth) / Decimal(before_transaction_Eth) < 0.2 ):
    if(Decimal(current_Eth) / Decimal(before_transaction_Eth) < -0.0000001):
        return False
    print('rugpull occur')
    return True
  else:
    return False

def get_rugpull_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction,index):
    if(index == 1):
      eth_amount = 'amount0'
      eth_amountIn = 'amount0In'
      eth_amountOut = 'amount0Out'
    else:
      eth_amount = 'amount1'
      eth_amountIn = 'amount1In'
      eth_amountOut = 'amount1Out'
    
    #각각 배열의 길이를 구해서 반복문 끝 조절
    mint_count = len(mint_data_transaction)
    swap_count = len(swap_data_transaction)
    burn_count = len(burn_data_transaction)

    
    #유동성에 남아있는 이더를 지속적으로 보면서 러그풀이 언제 발생하는지 탐지
    current_Liquidity_Eth = 0
    i,j,k = 0,0,0   #mint,swap,burn 배열의 인덱스
    while True:
        
      next_timestamp = min(get_timestamp(mint_data_transaction,i),get_timestamp(burn_data_transaction,k))

      #swap 인 경우 current_Eth 더하는 로직 / 러그풀 타임스탬프 체크
      while(get_timestamp(swap_data_transaction,j) < next_timestamp ):
        #swap이 제일 타임스탬프가 작은 경우니까 스왑에 맞게 amount +-를 하면 된다.
        before_transaction_Eth = current_Liquidity_Eth
        current_Liquidity_Eth = current_Liquidity_Eth + get_swap_amount(swap_data_transaction,j,eth_amountIn,eth_amountOut)
#        print('swap : ' + str(current_Liquidity_Eth))
        if(check_rugpull(before_transaction_Eth,current_Liquidity_Eth)):
          return get_timestamp(swap_data_transaction,j), Decimal(current_Liquidity_Eth / before_transaction_Eth) -1, True, before_transaction_Eth,current_Liquidity_Eth,'swap'
        j = j+1

      #mint 인 경우 curruent_Eth 더하는 로직
      if(next_timestamp == get_timestamp(mint_data_transaction,i)): #mint가 최소라면, + 한다.
        if(next_timestamp == '99999999999'):  #이건 rugpull이 없는 경우
          try:
              #여기까지 온거면 rugpull이 없는 경우인데 이때 네가지 케이스에 대한 예외케이스를 정의 해야한다.
              #Case 1 Swap/Burn이 없는 경우
              if(swap_count == 0 and burn_count == 0):
                  return mint_data_transaction[-1]['timestamp'],0, False, 0,0,''
              #Case 2 Swap이 없는 경우 
              if(swap_count == 0):
                  return max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp']),0,False, 0,0,''
              #Case 3 Burn이 없는 경우
              if(burn_count == 0):
                  return max(mint_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']),0,False, 0,0,''
              #Case 4 Mint/Swap/Burn이 다 있지만, Rugpull이 아닌 경우
              return max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']),0,False, 0,0,''
          except:
            return 'Error occur',100.0,False,1,1
        before_transaction_Eth = current_Liquidity_Eth
        current_Liquidity_Eth = current_Liquidity_Eth + Decimal(mint_data_transaction[i][eth_amount]) 
#        print(current_Liquidity_Eth)
        i = i+1

      #burn 인 경우 current_Eth 빼는 로직 / 러그풀 타임스탬프 체
      else:
        before_transaction_Eth = current_Liquidity_Eth
        current_Liquidity_Eth = current_Liquidity_Eth - Decimal(burn_data_transaction[k][eth_amount])
#        print('burn : ' + str(current_Liquidity_Eth))
        if(check_rugpull(before_transaction_Eth,current_Liquidity_Eth)):
          return get_timestamp(burn_data_transaction,k), Decimal(current_Liquidity_Eth / before_transaction_Eth) -1, True, before_transaction_Eth,current_Liquidity_Eth,'burn'
        k = k+1

def token_index(data):
    if(data['token0.name'] == 'Wrapped Ether'):
        return 1
    else:
        return 0


