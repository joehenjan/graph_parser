import tensorflow as tf 

def get_lstm_hw_weights(name, inputs_dim, units, batch_size, hidden_prob, beam_size=0, reuse=False):
    weights = {}
    with tf.variable_scope(name) as scope:
        if reuse:
            scope.reuse_variables()
        weights['theta_x_i'] = tf.get_variable('theta_x_i', [inputs_dim, units])
        weights['theta_x_f'] = tf.get_variable('theta_x_f', [inputs_dim, units])
        weights['theta_x_o'] = tf.get_variable('theta_x_o', [inputs_dim, units] )
        weights['theta_x_g'] = tf.get_variable('theta_x_g', [inputs_dim, units])
        weights['W_highway_x'] = tf.get_variable('W_highway_x', [inputs_dim, units])
        weights['W_input2output'] = tf.get_variable('W_input2output', [inputs_dim, units])
        weights['theta_h_i'] = tf.get_variable('theta_h_i', [units, units])
        weights['theta_h_f'] = tf.get_variable('theta_h_f', [units, units])
        weights['theta_h_o'] = tf.get_variable('theta_h_o', [units, units])
        weights['theta_h_g'] = tf.get_variable('theta_h_g', [units, units])
        weights['W_highway_h'] = tf.get_variable('W_highway_h', [units, units])
        weights['bias_i'] = tf.get_variable('bias_input', [units])
        weights['bias_f'] = tf.get_variable('bias_forget', [units], initializer = tf.constant_initializer(1))
        weights['bias_o'] = tf.get_variable('bias_output', [units])
        weights['bias_g'] = tf.get_variable('bias_extract', [units])
        weights['bias_highway'] = tf.get_variable('bias_highway', [units])
        dummy_dp = tf.ones([batch_size, units])
        weights['dropout'] = [tf.nn.dropout(dummy_dp, hidden_prob) for _ in xrange(5)]
        if beam_size > 0:
            dummy_dp = tf.ones([batch_size*beam_size, units])
            weights['dropout_post_first'] = [tf.nn.dropout(dummy_dp, hidden_prob) for _ in xrange(4)]
    return weights

def get_decoder_weights(weights, name, inputs_dim, units, reuse=False):
    with tf.variable_scope(name) as scope:
        if reuse:
            scope.reuse_variables()
    weights['theta_x_i'] = tf.get_variable('theta_x_i_decoder', [inputs_dim, units])
    weights['theta_x_f'] = tf.get_variable('theta_x_f_decoder', [inputs_dim, units])
    weights['theta_x_o'] = tf.get_variable('theta_x_o_decoder', [inputs_dim, units])
    weights['theta_x_g'] = tf.get_variable('theta_x_g_decoder', [inputs_dim, units])
    return weights

def lstm_hw(prev, x, weights, post_first=False, backward=False): # prev = c+h
    prev_c, prev_h = tf.unstack(prev, 2, 0) # [batch_size, units]
    if post_first:
        dropout = weights['dropout_post_first']
    else:
        dropout = weights['dropout']
    if backward:
        non_paddings = tf.reshape(x[1], [1, -1, 1])## [1, b, 1] 
        x = x[0] ## [b, d]
    i_gate = tf.nn.sigmoid(tf.matmul(prev_h*dropout[0], weights['theta_h_i'])+tf.matmul(x, weights['theta_x_i'])+weights['bias_i'])
    f_gate = tf.nn.sigmoid(tf.matmul(prev_h*dropout[1], weights['theta_h_f'])+tf.matmul(x, weights['theta_x_i'])+weights['bias_f'])
    o_gate = tf.nn.sigmoid(tf.matmul(prev_h*dropout[2], weights['theta_h_o'])+tf.matmul(x, weights['theta_x_o'])+weights['bias_o'])
    g_gate = tf.nn.tanh(tf.matmul(prev_h*dropout[3], weights['theta_h_g'])+tf.matmul(x, weights['theta_x_g'])+weights['bias_g'])
    c = (i_gate*g_gate + prev_c*f_gate)

    h = tf.nn.tanh(c)*o_gate
    r = tf.nn.sigmoid(tf.matmul(prev_h*dropout[4], weights['W_highway_h'])+tf.matmul(x, weights['W_highway_x'])+weights['bias_highway'])
    h = r*h+(1-r)*(tf.matmul(x, weights['W_input2output']))

    cell_hidden = tf.stack([c, h])
    #cell_hidden = tf.stack([prev_c, prev_h])
    if backward:
        cell_hidden = cell_hidden*non_paddings
    return  cell_hidden


