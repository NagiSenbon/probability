# Copyright 2018 The TensorFlow Probability Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Tests for Bijector."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Dependency imports
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp

tfd = tfp.distributions
tfb = tfd.bijectors


class InlineBijectorTest(tf.test.TestCase):
  """Tests correctness of the inline constructed bijector."""

  def testBijector(self):
    with self.test_session():
      exp = tfb.Exp()
      inline = tfb.Inline(
          forward_fn=tf.exp,
          inverse_fn=tf.log,
          inverse_log_det_jacobian_fn=lambda y: -tf.log(y),
          forward_log_det_jacobian_fn=lambda x: x,
          forward_min_event_ndims=0,
          name="exp")

      self.assertEqual(exp.name, inline.name)
      x = [[[1., 2.], [3., 4.], [5., 6.]]]
      y = np.exp(x)
      self.assertAllClose(y, inline.forward(x).eval())
      self.assertAllClose(x, inline.inverse(y).eval())
      self.assertAllClose(
          -np.sum(np.log(y), axis=-1),
          inline.inverse_log_det_jacobian(y, event_ndims=1).eval())
      self.assertAllClose(
          -inline.inverse_log_det_jacobian(y, event_ndims=1).eval(),
          inline.forward_log_det_jacobian(x, event_ndims=1).eval())

  def testShapeGetters(self):
    with self.test_session():
      bijector = tfb.Inline(
          forward_event_shape_tensor_fn=lambda x: tf.concat((x, [1]), 0),
          forward_event_shape_fn=lambda x: x.as_list() + [1],
          inverse_event_shape_tensor_fn=lambda x: x[:-1],
          inverse_event_shape_fn=lambda x: x[:-1],
          forward_min_event_ndims=0,
          name="shape_only")
      x = tf.TensorShape([1, 2, 3])
      y = tf.TensorShape([1, 2, 3, 1])
      self.assertAllEqual(y, bijector.forward_event_shape(x))
      self.assertAllEqual(
          y.as_list(),
          bijector.forward_event_shape_tensor(x.as_list()).eval())
      self.assertAllEqual(x, bijector.inverse_event_shape(y))
      self.assertAllEqual(
          x.as_list(),
          bijector.inverse_event_shape_tensor(y.as_list()).eval())


if __name__ == "__main__":
  tf.test.main()
