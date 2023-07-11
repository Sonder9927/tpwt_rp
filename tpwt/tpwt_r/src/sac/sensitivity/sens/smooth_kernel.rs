use ndarray::{prelude::*, Zip};

pub struct SmoothKernel {
    kernel: Array2<f32>,
}

impl SmoothKernel {
    pub fn new(smooth: i64, dt: f32) -> Self {
        let limit = 20;
        let kernel_part = Array2::from_shape_fn((limit + 1, limit + 1), |(i, j)| {
            let alpha = 1. / (smooth.pow(2) as f32);
            let x = i as f32 * dt;
            let y = j as f32 * dt;
            let distsq: f32 = alpha * (x.powi(2) + y.powi(2));
            if distsq < 80. {
                (-distsq).exp()
            } else {
                0.
            }
        });
        let kernel = Array2::from_shape_fn((limit * 2 + 1, limit * 2 + 1), |(i, j)| {
            let idiff = i.abs_diff(limit);
            // println_f!("idiff: {idiff}");
            let jdiff = j.abs_diff(limit);
            kernel_part[[idiff, jdiff]]
        });

        SmoothKernel { kernel }
    }

    pub fn forward(&self, input_matrix: ArrayView2<f32>) -> Array2<f32> {
        // padding
        let input_size = input_matrix.shape();
        let rows = input_size[0];
        let cols = input_size[1];
        let padded_matrix = self.padding(input_matrix);
        // one matrix for calculate mean of kernel
        let padded_one_matrix = self.padding(Array2::ones((rows, cols)).view());

        // output matrix
        let mut output_matrix = Array2::zeros((rows, cols));
        // conv
        let kernel_size = self.kernel.shape()[0];
        Zip::indexed(&mut output_matrix).par_for_each(|(i, j), output_elem| {
            let conv_slice = s![i..i + kernel_size, j..j + kernel_size];
            let wgt_view = padded_one_matrix.slice(conv_slice);
            let wgtsum: f32 = wgt_view
                .iter()
                .zip(self.kernel.iter())
                .map(|(&x, &w)| x * w)
                .sum();
            let input_view = padded_matrix.slice(conv_slice);
            *output_elem = input_view
                .iter()
                .zip(self.kernel.iter())
                .map(|(&x, &w)| x * w / wgtsum)
                .sum();
        });

        output_matrix
    }

    fn padding(&self, matrix: ArrayView2<f32>) -> Array2<f32> {
        let input_size = matrix.shape();
        let rows = input_size[0];
        let cols = input_size[1];
        let kernel_size = self.kernel.shape()[0];
        let padding = (kernel_size - 1) / 2;
        // padded matrix
        let mut padded_matrix = Array2::zeros((rows + 2 * padding, cols + 2 * padding));
        let mut padded_matrix_view =
            padded_matrix.slice_mut(s![padding..padding + rows, padding..padding + cols]);
        padded_matrix_view.assign(&matrix);

        padded_matrix
    }
}
